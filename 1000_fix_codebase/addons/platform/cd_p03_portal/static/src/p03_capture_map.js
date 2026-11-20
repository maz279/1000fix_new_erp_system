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

  /* M03 Service Logistics (Pick & Drop) — forms backed by an existing model; the rest stay 'not yet wired'. */
  M03: {
    forms: [{ en: 'Consignment (5 types)', bn: 'Consignment (5 types)' }, { en: 'Rider Shift Open/Close', bn: 'Rider Shift Open/Close' }, { en: 'Courier Booking', bn: 'Courier Booking' }, { en: 'Damage Claim', bn: 'Damage Claim' }],
    sub: {
      '1': ['Consignment (5 types)'],  // Consignment Creation (5 types)
    },
  },
  /* M04 Branch & Front-Desk — forms backed by an existing model; the rest stay 'not yet wired'. */
  M04: {
    forms: [{ en: 'Token Issue', bn: 'Token Issue' }, { en: 'Device Storage Assignment', bn: 'Device Storage Assignment' }, { en: 'Shift Open/Close', bn: 'Shift Open/Close' }, { en: 'Counter Sale', bn: 'Counter Sale' }, { en: 'Handover (ID verified)', bn: 'Handover (ID verified)' }],
    sub: {
      '1': ['Token Issue'],  // Token & Queue
      '8': ['Shift Open/Close'],  // Shift Operations
    },
  },
  /* M05 Remote Support & MSP — forms backed by an existing model; the rest stay 'not yet wired'. */
  M05: {
    forms: [{ en: 'Remote Session (consent recorded)', bn: 'Remote Session (consent recorded)' }, { en: 'MSP Ticket', bn: 'MSP Ticket' }, { en: 'Change Record', bn: 'Change Record' }, { en: 'Maintenance Window', bn: 'Maintenance Window' }],
    sub: {
      '1': ['Remote Session (consent recorded)'],  // Remote Sessions
    },
  },
  /* M06 Data Services & Recovery — forms backed by an existing model; the rest stay 'not yet wired'. */
  M06: {
    forms: [{ en: 'Recovery Case', bn: 'Recovery Case' }, { en: 'Media Intake (sealed)', bn: 'Media Intake (sealed)' }, { en: 'Firm Quotation', bn: 'Firm Quotation' }, { en: 'Destruction Request (dual control)', bn: 'Destruction Request (dual control)' }],
    sub: {
      '1': ['Recovery Case'],  // Case Management (7 specialisms)
    },
  },
  /* M08 Contract Lifecycle (AMC) — forms backed by an existing model; the rest stay 'not yet wired'. */
  M08: {
    forms: [{ en: 'Contract (14 families)', bn: 'Contract (14 families)' }, { en: 'Amendment', bn: 'Amendment' }, { en: 'Asset Attach/Detach', bn: 'Asset Attach/Detach' }, { en: 'Renewal Quote', bn: 'Renewal Quote' }, { en: 'PM Schedule', bn: 'PM Schedule' }],
    sub: {
      '1': ['Contract (14 families)'],  // Template-Driven Creation
      '6': ['PM Schedule'],  // PM Schedules
    },
  },
  /* M09 Warranty & Claims — forms backed by an existing model; the rest stay 'not yet wired'. */
  M09: {
    forms: [{ en: 'Brand Claim', bn: 'Brand Claim' }, { en: 'Protection Policy', bn: 'Protection Policy' }, { en: 'Claim Appeal', bn: 'Claim Appeal' }, { en: 'Recall Campaign', bn: 'Recall Campaign' }],
    sub: {
      '8': ['Brand Claim'],  // Brand Submission
    },
  },
  /* M11 Pricing & Rate Cards — forms backed by an existing model; the rest stay 'not yet wired'. */
  M11: {
    forms: [{ en: 'Price Book', bn: 'Price Book' }, { en: 'Rate Card', bn: 'Rate Card' }, { en: 'Discount Policy', bn: 'Discount Policy' }, { en: 'Promotion', bn: 'Promotion' }, { en: 'Price Simulation Request', bn: 'Price Simulation Request' }],
    sub: {
      '3': ['Rate Card'],  // Rate Cards
    },
  },
  /* M12 Marketplace & Sellers — forms backed by an existing model; the rest stay 'not yet wired'. */
  M12: {
    forms: [{ en: 'Seller Application', bn: 'Seller Application' }, { en: 'Listing', bn: 'Listing' }, { en: 'Payout Run', bn: 'Payout Run' }, { en: 'Dispute Case', bn: 'Dispute Case' }],
    sub: {
      '1': ['Seller Application'],  // Seller Registration & KYC
    },
  },
  /* M13 Rental & EaaS — forms backed by an existing model; the rest stay 'not yet wired'. */
  M13: {
    forms: [{ en: 'Reservation', bn: 'Reservation' }, { en: 'Rental Agreement (e-sign)', bn: 'Rental Agreement (e-sign)' }, { en: 'Condition Report', bn: 'Condition Report' }, { en: 'Damage Assessment', bn: 'Damage Assessment' }],
    sub: {
      '2': ['Reservation'],  // Availability & Reservation
      '5': ['Damage Assessment'],  // Condition & Damage
    },
  },
  /* M14 Trade-In & Refurbishment — forms backed by an existing model; the rest stay 'not yet wired'. */
  M14: {
    forms: [{ en: 'Trade-In Request', bn: 'Trade-In Request' }, { en: 'Valuation Offer', bn: 'Valuation Offer' }, { en: 'Refurb Work Order', bn: 'Refurb Work Order' }, { en: 'Grading Result', bn: 'Grading Result' }],
    sub: {
      '1': ['Trade-In Request'],  // Intake (5 channels)
      '7': ['Refurb Work Order'],  // Refurbishment Orders
    },
  },
  /* M16 Procurement & Sourcing — forms backed by an existing model; the rest stay 'not yet wired'. */
  M16: {
    forms: [{ en: 'Purchase Requisition', bn: 'Purchase Requisition' }, { en: 'RFQ', bn: 'RFQ' }, { en: 'Purchase Order', bn: 'Purchase Order' }, { en: 'GRN', bn: 'GRN' }, { en: 'RTV Request', bn: 'RTV Request' }],
    sub: {
      '2': ['Purchase Requisition'],  // Requisition & Approval
      '5': ['Purchase Order'],  // PO Lifecycle
    },
  },
  /* M17 Device & Asset Registry — forms backed by an existing model; the rest stay 'not yet wired'. */
  M17: {
    forms: [{ en: 'Asset (6 identifiers)', bn: 'Asset (6 identifiers)' }, { en: 'Estate Assignment', bn: 'Estate Assignment' }, { en: 'Ownership Transfer', bn: 'Ownership Transfer' }, { en: 'Condition Grading', bn: 'Condition Grading' }],
    sub: {
      '1': ['Asset (6 identifiers)'],  // Identity & Resolution
      '3': ['Ownership Transfer'],  // Ownership & Custody
    },
  },
  /* M18 E-Waste & Recycling — forms backed by an existing model; the rest stay 'not yet wired'. */
  M18: {
    forms: [{ en: 'Collection Booking', bn: 'Collection Booking' }, { en: 'Triage Decision', bn: 'Triage Decision' }, { en: 'Batch Transfer Note', bn: 'Batch Transfer Note' }, { en: 'Disposal Record', bn: 'Disposal Record' }],
    sub: {
      '1': ['Collection Booking'],  // Collection Network
    },
  },
  /* M20 AR, Invoicing & Collections — forms backed by an existing model; the rest stay 'not yet wired'. */
  M20: {
    forms: [{ en: 'Invoice Request', bn: 'Invoice Request' }, { en: 'Receipt', bn: 'Receipt' }, { en: 'Credit Note', bn: 'Credit Note' }, { en: 'Refund', bn: 'Refund' }, { en: 'Payment Link', bn: 'Payment Link' }],
    sub: {
      '9': ['Credit Note'],  // Credit Notes & Refunds
    },
  },
  /* M22 Learning & Certification — forms backed by an existing model; the rest stay 'not yet wired'. */
  M22: {
    forms: [{ en: 'Certification', bn: 'Certification' }, { en: 'Course', bn: 'Course' }, { en: 'Learning Path', bn: 'Learning Path' }, { en: 'Assessment', bn: 'Assessment' }],
    sub: {
      '3': ['Certification'],  // Certification Register
      '4': ['Course'],  // Training Delivery
    },
  },
  /* M23 Quality Management (ISO) — forms backed by an existing model; the rest stay 'not yet wired'. */
  M23: {
    forms: [{ en: 'NCR', bn: 'NCR' }, { en: 'CAPA', bn: 'CAPA' }, { en: 'Audit Finding', bn: 'Audit Finding' }, { en: 'Checklist Template', bn: 'Checklist Template' }],
    sub: {
      '4': ['NCR'],  // NCR Management
      '5': ['CAPA'],  // RCA & CAPA
    },
  },
  /* M24 Documents & E-Signature — forms backed by an existing model; the rest stay 'not yet wired'. */
  M24: {
    forms: [{ en: 'Upload', bn: 'Upload' }, { en: 'Signature Envelope', bn: 'Signature Envelope' }, { en: 'Share Token', bn: 'Share Token' }, { en: 'Retention Policy', bn: 'Retention Policy' }],
    sub: {
      '5': ['Signature Envelope'],  // E-Signature
      '6': ['Retention Policy'],  // Retention & Holds
    },
  },
  /* M29 Identity, Access & Security — forms backed by an existing model; the rest stay 'not yet wired'. */
  M29: {
    forms: [{ en: 'User', bn: 'User' }, { en: 'Role', bn: 'Role' }, { en: 'Record Rule', bn: 'Record Rule' }, { en: 'Access Request', bn: 'Access Request' }],
    sub: {
      '3': ['Role'],  // Roles & Record Rules
    },
  },
  /* M30 Platform Administration — forms backed by an existing model; the rest stay 'not yet wired'. */
  M30: {
    forms: [{ en: 'Branch', bn: 'Branch' }, { en: 'Config Parameter', bn: 'Config Parameter' }, { en: 'Feature Flag', bn: 'Feature Flag' }, { en: 'Announcement', bn: 'Announcement' }],
    sub: {
      '1': ['Branch'],  // Entity & Branch Register
      '4': ['Feature Flag'],  // Feature Flags
    },
  },
  /* M31 Workshop & Depot Repair — forms backed by an existing model; the rest stay 'not yet wired'. */
  M31: {
    forms: [{ en: 'Repair Order', bn: 'Repair Order' }, { en: 'Bench Allocation', bn: 'Bench Allocation' }, { en: 'Test Protocol Result', bn: 'Test Protocol Result' }, { en: 'Workshop Transfer', bn: 'Workshop Transfer' }],
    sub: {
      '1': ['Repair Order'],  // Repair Order Creation
    },
  },
  /* M33 Customer & Party Master — forms backed by an existing model; the rest stay 'not yet wired'. */
  M33: {
    forms: [{ en: 'Party (multi-role)', bn: 'Party (multi-role)' }, { en: 'Address with GPS', bn: 'Address with GPS' }, { en: 'Identity Document', bn: 'Identity Document' }, { en: 'Credit Profile', bn: 'Credit Profile' }, { en: 'Merge Request', bn: 'Merge Request' }],
    sub: {
      '5': ['Identity Document'],  // Identity & OTP
    },
  },
  /* M34 CX, Feedback & Complaints — forms backed by an existing model; the rest stay 'not yet wired'. */
  M34: {
    forms: [{ en: 'Survey', bn: 'Survey' }, { en: 'Complaint', bn: 'Complaint' }, { en: 'Goodwill Credit', bn: 'Goodwill Credit' }, { en: 'Detractor Follow-up', bn: 'Detractor Follow-up' }],
    sub: {
      '5': ['Complaint'],  // Complaint Management
    },
  },
  /* M35 Marketing Campaigns — forms backed by an existing model; the rest stay 'not yet wired'. */
  M35: {
    forms: [{ en: 'Campaign', bn: 'Campaign' }, { en: 'Journey (multi-step)', bn: 'Journey (multi-step)' }, { en: 'Offer', bn: 'Offer' }, { en: 'Creative Asset', bn: 'Creative Asset' }],
    sub: {
      '1': ['Campaign'],  // Campaign Planning & Approval
    },
  },
  /* M36 Quotations & Tenders — forms backed by an existing model; the rest stay 'not yet wired'. */
  M36: {
    forms: [{ en: 'Estimate', bn: 'Estimate' }, { en: 'Quotation (versioned)', bn: 'Quotation (versioned)' }, { en: 'Tender Bid', bn: 'Tender Bid' }, { en: 'Counter-Offer', bn: 'Counter-Offer' }],
    sub: {
      '1': ['Estimate'],  // Estimate Build-Up
    },
  },
  /* M37 Product & Service Catalogue — forms backed by an existing model; the rest stay 'not yet wired'. */
  M37: {
    forms: [{ en: 'Catalogue Item (9 types)', bn: 'Catalogue Item (9 types)' }, { en: 'Service Definition', bn: 'Service Definition' }, { en: 'rBOM Line', bn: 'rBOM Line' }, { en: 'Fault Code', bn: 'Fault Code' }, { en: 'Protection Product Template', bn: 'Protection Product Template' }],
    sub: {
      '1': ['Catalogue Item (9 types)'],  // Unified Item Master
    },
  },
  /* M38 E-Commerce Storefront — forms backed by an existing model; the rest stay 'not yet wired'. */
  M38: {
    forms: [{ en: 'Online Order', bn: 'Online Order' }, { en: 'RMA Request', bn: 'RMA Request' }, { en: 'Storefront Slot', bn: 'Storefront Slot' }, { en: 'Delivery Slot', bn: 'Delivery Slot' }],
    sub: {
      '7': ['RMA Request'],  // Returns & RMA
    },
  },
  /* M39 Subscriptions & Recurring — forms backed by an existing model; the rest stay 'not yet wired'. */
  M39: {
    forms: [{ en: 'Subscription', bn: 'Subscription' }, { en: 'Billing Schedule', bn: 'Billing Schedule' }, { en: 'Plan Change', bn: 'Plan Change' }, { en: 'Dunning Step', bn: 'Dunning Step' }],
    sub: {
      '1': ['Subscription'],  // Subscription Object
    },
  },
  /* M40 Partner & Channel — forms backed by an existing model; the rest stay 'not yet wired'. */
  M40: {
    forms: [{ en: 'Partner', bn: 'Partner' }, { en: 'Deal Registration', bn: 'Deal Registration' }, { en: 'Rebate Scheme', bn: 'Rebate Scheme' }, { en: 'Franchise Agreement', bn: 'Franchise Agreement' }],
    sub: {
      '1': ['Partner'],  // Partner Master
    },
  },
  /* M41 Warehouse Management — forms backed by an existing model; the rest stay 'not yet wired'. */
  M41: {
    forms: [{ en: 'Bin', bn: 'Bin' }, { en: 'Wave Template', bn: 'Wave Template' }, { en: 'Dock Appointment', bn: 'Dock Appointment' }, { en: 'Packing Station Config', bn: 'Packing Station Config' }],
    sub: {
      '1': ['Bin'],  // Physical Structure
    },
  },
  /* M44 Import & Trade Compliance — forms backed by an existing model; the rest stay 'not yet wired'. */
  M44: {
    forms: [{ en: 'Import Order', bn: 'Import Order' }, { en: 'LC Application', bn: 'LC Application' }, { en: 'HS Ruling Request', bn: 'HS Ruling Request' }, { en: 'Bill of Entry', bn: 'Bill of Entry' }],
    sub: {
      '1': ['Import Order'],  // Import Order Lifecycle
    },
  },
  /* M45 Enterprise Assets & Test Equipment — forms backed by an existing model; the rest stay 'not yet wired'. */
  M45: {
    forms: [{ en: 'Equipment', bn: 'Equipment' }, { en: 'Calibration Record', bn: 'Calibration Record' }, { en: 'Issue/Return', bn: 'Issue/Return' }, { en: 'Write-Off', bn: 'Write-Off' }],
    sub: {
      '1': ['Equipment'],  // Register & Classification
      '4': ['Calibration Record'],  // Calibration Management
    },
  },
  /* M47 Facility & Branch Infrastructure — forms backed by an existing model; the rest stay 'not yet wired'. */
  M47: {
    forms: [{ en: 'Site', bn: 'Site' }, { en: 'Lease', bn: 'Lease' }, { en: 'Licence', bn: 'Licence' }, { en: 'Facility Work Order', bn: 'Facility Work Order' }, { en: 'Safety Inspection', bn: 'Safety Inspection' }],
    sub: {
      '1': ['Site'],  // Site Register
      '7': ['Facility Work Order'],  // Work Orders
      '8': ['Safety Inspection'],  // Safety & Security
    },
  },
  /* M52 AP & Employee Expense — forms backed by an existing model; the rest stay 'not yet wired'. */
  M52: {
    forms: [{ en: 'Vendor Bill', bn: 'Vendor Bill' }, { en: 'Expense Claim', bn: 'Expense Claim' }, { en: 'Employee Advance', bn: 'Employee Advance' }, { en: 'Debit Note', bn: 'Debit Note' }],
    sub: {
      '1': ['Vendor Bill'],  // Invoice Capture
      '7': ['Expense Claim'],  // Employee Expenses
    },
  },
  /* M53 Revenue Recognition & Settlement — forms backed by an existing model; the rest stay 'not yet wired'. */
  M53: {
    forms: [{ en: 'Revenue Schedule', bn: 'Revenue Schedule' }, { en: 'Payout Run', bn: 'Payout Run' }, { en: 'Clawback', bn: 'Clawback' }, { en: 'Commission Scheme', bn: 'Commission Scheme' }],
    sub: {
      '7': ['Payout Run'],  // Seller Settlement
      '8': ['Payout Run'],  // Partner Payouts
    },
  },
  /* M54 Costing, Budget & FP&A — forms backed by an existing model; the rest stay 'not yet wired'. */
  M54: {
    forms: [{ en: 'Budget Version', bn: 'Budget Version' }, { en: 'Allocation Rule', bn: 'Allocation Rule' }, { en: 'Scenario', bn: 'Scenario' }],
    sub: {
      '6': ['Budget Version'],  // Budgeting
    },
  },
  /* M55 Time, Attendance & Scheduling — forms backed by an existing model; the rest stay 'not yet wired'. */
  M55: {
    forms: [{ en: 'Leave Request', bn: 'Leave Request' }, { en: 'Roster', bn: 'Roster' }, { en: 'Shift Pattern', bn: 'Shift Pattern' }, { en: 'Exception Regularisation', bn: 'Exception Regularisation' }],
    sub: {
      '3': ['Leave Request'],  // Leave
      '5': ['Shift Pattern'],  // Shifts & Rosters
    },
  },
  /* M58 Talent Acquisition — forms backed by an existing model; the rest stay 'not yet wired'. */
  M58: {
    forms: [{ en: 'Requisition', bn: 'Requisition' }, { en: 'Candidate', bn: 'Candidate' }, { en: 'Interview Evaluation', bn: 'Interview Evaluation' }, { en: 'Offer', bn: 'Offer' }],
    sub: {
      '1': ['Requisition'],  // Workforce Planning & Requisition
      '2': ['Candidate'],  // Sourcing
    },
  },
  /* M59 Health, Safety & Wellbeing — forms backed by an existing model; the rest stay 'not yet wired'. */
  M59: {
    forms: [{ en: 'Incident Report', bn: 'Incident Report' }, { en: 'JSA', bn: 'JSA' }, { en: 'PPE Issue', bn: 'PPE Issue' }, { en: 'Return-to-Work', bn: 'Return-to-Work' }],
    sub: {
      '3': ['Incident Report'],  // Incident Management
    },
  },
  /* M60 Governance, Risk & Compliance — forms backed by an existing model; the rest stay 'not yet wired'. */
  M60: {
    forms: [{ en: 'Risk', bn: 'Risk' }, { en: 'Control Test', bn: 'Control Test' }, { en: 'Licence', bn: 'Licence' }, { en: 'Policy', bn: 'Policy' }, { en: 'Whistleblow Report', bn: 'Whistleblow Report' }],
    sub: {
      '1': ['Risk'],  // Risk Register
    },
  },
  /* M61 Knowledge & Technical Library — forms backed by an existing model; the rest stay 'not yet wired'. */
  M61: {
    forms: [{ en: 'Article', bn: 'Article' }, { en: 'Troubleshooting Tree', bn: 'Troubleshooting Tree' }, { en: 'Bulletin', bn: 'Bulletin' }],
    sub: {
      '1': ['Article'],  // Authoring & Versioning
    },
  },
  /* M62 Data Platform & Governance — forms backed by an existing model; the rest stay 'not yet wired'. */
  M62: {
    forms: [{ en: 'Data Contract', bn: 'Data Contract' }, { en: 'Metric Definition', bn: 'Metric Definition' }, { en: 'Quality Test', bn: 'Quality Test' }],
    sub: {
      '5': ['Quality Test'],  // Quality & Observability
    },
  },
  /* M63 Process Automation — forms backed by an existing model; the rest stay 'not yet wired'. */
  M63: {
    forms: [{ en: 'Workflow Definition', bn: 'Workflow Definition' }, { en: 'Approval Chain', bn: 'Approval Chain' }, { en: 'Business Rule', bn: 'Business Rule' }],
    sub: {
      '3': ['Approval Chain'],  // DoA Matrix
    },
  },
  /* M64 Master Data Management — forms backed by an existing model; the rest stay 'not yet wired'. */
  M64: {
    forms: [{ en: 'Steward Request', bn: 'Steward Request' }, { en: 'DQ Rule', bn: 'DQ Rule' }, { en: 'Code List Entry', bn: 'Code List Entry' }],
    sub: {
      '2': ['Steward Request'],  // Stewardship
    },
  },
  /* M66 Internal IT Service — forms backed by an existing model; the rest stay 'not yet wired'. */
  M66: {
    forms: [{ en: 'Incident', bn: 'Incident' }, { en: 'Change', bn: 'Change' }, { en: 'Asset', bn: 'Asset' }, { en: 'Service Request', bn: 'Service Request' }],
    sub: {
      '2': ['Incident'],  // Incident & Problem
    },
  },
  /* M67 Projects & Portfolio — forms backed by an existing model; the rest stay 'not yet wired'. */
  M67: {
    forms: [{ en: 'Project (6 types)', bn: 'Project (6 types)' }, { en: 'Milestone', bn: 'Milestone' }, { en: 'Task', bn: 'Task' }, { en: 'Stage Gate Review', bn: 'Stage Gate Review' }],
    sub: {
      '1': ['Project (6 types)'],  // Project Object & WBS
      '5': ['Milestone'],  // Milestone Billing
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
