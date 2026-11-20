/** @odoo-module **/

/* =====================================================================
 * 1000 FiX ERP — Complete 67-Module Metadata & Data Schema Dictionary
 * Port of Prototype UX (FIX-UXD-2026-001) for 1000 FiX Services Ltd.
 * Full Human-Readable Titles for all 67 Modules across 11 Business Areas (A02–A12).
 * ===================================================================== */

export const P03_AREAS = [
  { id: 'A02', key: 'service',    en: 'Service Operations',      bn: 'সার্ভিস অপারেশন',          mods: ['M01','M02','M31','M03','M04','M05','M06'] },
  { id: 'A03', key: 'customer',   en: 'Customer Experience',     bn: 'গ্রাহক অভিজ্ঞতা',           mods: ['M33','M07','M10','M34','M27','M32','M35'] },
  { id: 'A04', key: 'commercial', en: 'Commercial & Revenue',    bn: 'বাণিজ্যিক ও রাজস্ব',        mods: ['M37','M11','M36','M08','M09','M39','M38','M12','M40'] },
  { id: 'A05', key: 'circular',   en: 'Circular Economy',        bn: 'সার্কুলার ইকোনমি',         mods: ['M13','M14','M18'] },
  { id: 'A06', key: 'supply',     en: 'Supply Chain',            bn: 'সরবরাহ শৃঙ্খল',             mods: ['M15','M41','M16','M42','M43','M44'] },
  { id: 'A07', key: 'assets',     en: 'Assets & Facilities',     bn: 'সম্পদ ও সুবিধা',            mods: ['M17','M45','M46','M47','M48'] },
  { id: 'A08', key: 'finance',    en: 'Finance & Treasury',      bn: 'অর্থ ও কোষাগার',            mods: ['M19','M20','M52','M50','M51','M53','M49','M54'] },
  { id: 'A09', key: 'people',     en: 'People & Workforce',      bn: 'জনবল',                      mods: ['M21','M55','M56','M57','M22','M58','M59'] },
  { id: 'A10', key: 'quality',    en: 'Quality & Governance',    bn: 'গুণগতমান ও গভর্নেন্স',      mods: ['M23','M60','M24','M61'] },
  { id: 'A11', key: 'insight',    en: 'Insights & Intelligence', bn: 'বিশ্লেষণ ও বুদ্ধিমত্তা',     mods: ['M25','M26','M62','M63'] },
  { id: 'A12', key: 'platform',   en: 'Platform & Technology',   bn: 'প্ল্যাটফর্ম ও প্রযুক্তি',    mods: ['M28','M29','M30','M64','M65','M66','M67'] }
];

/* =====================================================================
 * P03 · The 15 Role Workspaces & Consoles (RP-004 §4.2, TR-007..TR-021)
 * Tailored for 150–250 back-office and branch staff across Bangladesh.
 * ===================================================================== */
export const P03_ROLES = [
  { id: 'service_intake', code: 'R08', en: 'Service Intake Counter', bn: 'সার্ভিস ইনটেক কাউন্টার', icon: '📥', desc: 'Walk-in customer token queue, rapid intake registration (<3 min), and device check-in.' },
  { id: 'dispatch_manager', code: 'R07', en: 'Dispatch & Live Map', bn: 'ডিসপ্যাচ ও লাইভ ম্যাপ', icon: '⚡', desc: 'Interactive GPS vector map, SLA risk countdowns, and automated field technician allocation.' },
  { id: 'branch_manager', code: 'R06', en: 'Branch Operations Console', bn: 'শাখা পরিচালনা কনসোল', icon: '🏢', desc: 'Own-branch daily intake, cash & bKash register, WIP ageing, and ready-for-collection shelf.' },
  { id: 'workshop_supervisor', code: 'R09', en: 'Workshop & Depot Repair', bn: 'ওয়ার্কশপ ও ডিপো মেরামত', icon: '🔧', desc: '8-station bench board, parts & estimate holds, QC inspection queue, and rework detection.' },
  { id: 'field_technician', code: 'R09-F', en: 'Field Service Technician', bn: 'ফিল্ড সার্ভিস টেকনিশিয়ান', icon: '🛵', desc: 'Day queue, Dhaka Circle geofenced clock-in, van stock barcode scanning, and e-signatures.' },
  { id: 'inventory_keeper', code: 'R17', en: 'Inventory & Store Keeper', bn: 'ইনভেন্টরি ও স্টোর কিপার', icon: '📦', desc: 'Warehouse bin cards, stockout prevention, van replenishment, and RMA quarantine.' },
  { id: 'procurement_officer', code: 'R19', en: 'Procurement & Purchasing', bn: 'ক্রয় ও সংগ্রহ কর্মকর্তা', icon: '🛒', desc: 'Purchase orders, supplier lead times, buffer stock calculations, and landed cost reconciliation.' },
  { id: 'finance_officer', code: 'R26', en: 'Finance & Mushak 6.3', bn: 'অর্থ ও মূসক ৬.৩ চালান', icon: '💰', desc: 'Statutory Mushak 6.3 VAT tax invoices, NBR compliance, and collection reconciliation.' },
  { id: 'hr_payroll', code: 'R30', en: 'People & Workforce HR', bn: 'এইচআর ও কর্মী শিফট', icon: '👥', desc: 'Staff shifts, biometric attendance logs, field overtime, and skill certification matrix.' },
  { id: 'quality_auditor', code: 'R32', en: 'Quality & ISO 9001 Audit', bn: 'কোয়ালিটি ও আইএসও অডিট', icon: '🔬', desc: 'ISO 9001:2015 audit checklists, repeat-repair investigation, and equipment calibration.' },
  { id: 'contact_centre_agent', code: 'R08-C', en: 'Contact Centre & Hotline', bn: 'হটলাইন ১৬৭৪৩ ও কন্টাক্ট সেন্টার', icon: '🎧', desc: 'Hotline 16743 queue, omnichannel customer chat, ticket resolution, and callback scheduling.' },
  { id: 'account_manager', code: 'R22', en: 'Corporate B2B & Contracts', bn: 'কর্পোরেট চুক্তি ও এএমসি', icon: '💼', desc: 'Enterprise client estates, SLA credit penalties, bulk service orders, and AMC billing.' },
  { id: 'marketplace_ops', code: 'R24', en: 'Marketplace & Vendor Ops', bn: 'মার্কেটপ্লেস ও বিক্রেতা', icon: '🛍️', desc: 'Verified parts merchant onboarding, escrow settlement, disputes, and parts catalogue sync.' },
  { id: 'rider_logistics', code: 'R20', en: 'Rider & Logistics Fleet', bn: 'রাইডার ও লজিস্টিকস বহর', icon: '🚚', desc: 'Hub-to-hub manifests, pick-and-drop logistics, parcel transit fleet tracking.' },
  { id: 'system_admin', code: 'R33', en: 'System & Security Admin', bn: 'সিস্টেম ও সিকিউরিটি অ্যাডমিন', icon: '🛡️', desc: 'RBAC permissions, immutable audit logs, server telemetry, and PDPA data residency.' }
];

export const P03_MODULES = {
  /* ============ A02 · SERVICE OPERATIONS ============================== */
  M01: {
    area: 'A02',
    code: 'M01',
    en: 'Service Requests & Orders',
    title: 'M01 · Service Requests & Orders',
    bn: 'সার্ভিস অর্ডার',
    icon: '📋',
    desc: 'Master record of every service need from 12 intake channels — lifecycle, entitlement, estimates, SLA.',
    kpis: [
      { l: 'Open Orders' },
      { l: 'SLA At-Risk' },
      { l: 'TAT < 24h (IT)' },
      { l: 'Estimate Conv.' },
      { l: 'Intake < 3 min' },
      { l: 'Rework Rate' }
    ],
    groups: [
      {
        en: 'Intake & Channels',
        screens: [
          { id: 'M01-board', en: 'Order Operations Board', bn: 'অর্ডার অপারেশন্স বোর্ড', t: 'd' },
          { id: 'M01-all', en: 'All Service Orders', bn: 'সকল সার্ভিস অর্ডার', t: 'g' },
          { id: 'M01-intake', en: 'Omni-Channel Intake', bn: 'অমনি-চ্যানেল ইনটেক', t: 'c' },
          { id: 'M01-channels', en: 'Channel Performance', bn: 'চ্যানেল পারফরম্যান্স', t: 'r' },
          { id: 'M01-hotline', en: 'Hotline 16743 Queue', bn: 'হটলাইন ১৬৭৪৩ কিউ', t: 'g' }
        ]
      },
      {
        en: 'Order Lifecycle',
        screens: [
          { id: 'M01-order', en: 'Service Order Record', bn: 'সার্ভিস অর্ডার নথি', t: 'f' },
          { id: 'M01-types', en: 'Order Types (12 Streams)', bn: 'অর্ডার ক্যাটাগরি', t: 'g' },
          { id: 'M01-wip', en: 'WIP & Ageing Analysis', bn: 'চলমান কাজ ও এজিং', t: 'r' },
          { id: 'M01-holds', en: 'Hold Management', bn: 'হোল্ড ব্যবস্থাপনা', t: 'g' },
          { id: 'M01-rework', en: 'Rework Detection', bn: 'রিওয়ার্ক শনাক্তকরণ', t: 'g' }
        ]
      },
      {
        en: 'Diagnosis & Estimates',
        screens: [
          { id: 'M01-templates', en: 'Diagnostic Templates', bn: 'ডায়াগনস্টিক টেমপ্লেট', t: 'g' },
          { id: 'M01-fault', en: 'Fault & Symptom Coding', bn: 'ত্রুটি ও লক্ষণ কোডিং', t: 'g' },
          { id: 'M01-estimates', en: 'Estimates & Approvals', bn: 'অনুমান ও অনুমোদন', t: 'g' },
          { id: 'M01-thresholds', en: 'Approval Thresholds', bn: 'অনুমোদন সীমা', t: 'g' }
        ]
      },
      {
        en: 'Entitlement & SLA',
        screens: [
          { id: 'M01-entitle', en: 'Entitlement Evaluation', bn: 'সুবিধা ও ওয়ারেন্টি যাচাই', t: 'g' },
          { id: 'M01-sla', en: 'SLA Policies & Clocks', bn: 'এসএলএ পলিসি ও কাউন্টডাউন', t: 'g' },
          { id: 'M01-esc', en: 'Escalation Rules', bn: 'এসকেলেশন রুলস', t: 'g' },
          { id: 'M01-sla-rep', en: 'SLA Compliance Report', bn: 'এসএলএ সম্মতি রিপোর্ট', t: 'r' }
        ]
      },
      {
        en: 'Quality & Release',
        screens: [
          { id: 'M01-qc', en: 'QC Checkpoints & Inspection', bn: 'কিউসি পরিদর্শন', t: 'g' },
          { id: 'M01-reports', en: 'Service Reports & Proof', bn: 'সার্ভিস রিপোর্ট ও প্রমাণক', t: 'g' },
          { id: 'M01-rwty', en: 'Repair Warranty Issuance', bn: 'মেরামত ওয়ারেন্টি সার্টিফিকেট', t: 'g' }
        ]
      }
    ],
    reports: [
      'Daily Intake by Channel', 'WIP Ageing by Branch', 'SLA Compliance & Escalations',
      'Estimate Conversion Funnel', 'Rework & Repeat-Fault Analysis', 'Order Cycle-Time (TAT) Distribution', 'Uncollected Device Register'
    ],
    forms: [
      'New Service Order (12 channels, 34 fields)', 'Diagnostic Estimate Request', 'Hold / Release Reason', 'QC Checklist Inspection'
    ],
    cross: [
      'M02 Field Dispatch Handoff', 'M31 Workshop Routing', 'M09 Brand Warranty Check', 'M20 Mushak 6.3 Invoicing', 'M17 Device History'
    ],
    freg: {
      src: 128,
      sub: [
        ['1', 'Omni-Channel Intake (12 channels)', 14],
        ['2', 'Lifecycle State Machine & Stepper', 9],
        ['3', 'Entitlement Evaluation & SLA Clock', 8],
        ['4', 'Complaint & Fault Taxonomy Coding', 10],
        ['5', 'Diagnostic Templates & Benchmarks', 7],
        ['6', 'Estimate & Customer Approval Loop', 12],
        ['7', 'Assignment & Field Dispatch Handoff', 6],
        ['8', 'SLA Policy, Clock & Escalations', 13],
        ['9', 'Customer Hold & Release Management', 5],
        ['10', 'QC Checkpoints & Rework Detection', 11],
        ['11', 'Service Reports & Repair Warranty', 12],
        ['12', 'Operations Boards & WIP Analysis', 11],
        ['13', 'API & Domain Event Broadcasting', 10]
      ]
    }
  },

  M02: {
    area: 'A02',
    code: 'M02',
    en: 'Field Service & Dispatch',
    title: 'M02 · Field Service & Dispatch',
    bn: 'ফিল্ড সার্ভিস ও ডিসপ্যাচ',
    icon: '🚐',
    desc: 'AI dispatch board, route optimisation, technician app (24h offline), GPS tracking, field evidence & payments.',
    kpis: [
      { l: 'Jobs / Tech / Day' },
      { l: 'Auto-Assignment' },
      { l: 'On-Time Arrival' },
      { l: 'Travel Time Share' },
      { l: 'Unassigned > 15m' },
      { l: 'Offline Sync Health' }
    ],
    groups: [
      {
        en: 'Dispatch Console',
        screens: [
          { id: 'M02-dispatch', en: 'Dispatch Board (Live AI)', bn: 'লাইভ এআই ডিসপ্যাচ বোর্ড', t: 'd' },
          { id: 'M02-map', en: 'Live Technician GPS Map', bn: 'লাইভ টেকনিশিয়ান ম্যাপ', t: 'd' },
          { id: 'M02-unassigned', en: 'Unassigned Jobs Queue', bn: 'অনির্ধারিত কাজের সারি', t: 'g' },
          { id: 'M02-sla-risk', en: 'SLA Risk & Escalation Board', bn: 'এসএলএ ঝুঁকি বোর্ড', t: 'g' }
        ]
      },
      {
        en: 'Work Orders',
        screens: [
          { id: 'M02-wo', en: 'Field Work Orders', bn: 'ফিল্ড ওয়ার্ক অর্ডার', t: 'g' },
          { id: 'M02-record', en: 'Work Order Record View', bn: 'ওয়ার্ক অর্ডার নথি', t: 'f' },
          { id: 'M02-exceptions', en: 'Field Job Exceptions', bn: 'ফিল্ড ব্যতিক্রম', t: 'g' },
          { id: 'M02-crews', en: 'Multi-Tech Crews', bn: 'ক্রু নিয়োগ', t: 'g' }
        ]
      },
      {
        en: 'Routing & Territories',
        screens: [
          { id: 'M02-zones', en: 'Territory Zones & Geofences', bn: 'জোন ও জিওফেন্স', t: 'g' },
          { id: 'M02-routes', en: 'Route Optimization Engine', bn: 'রুট অপ্টিমাইজেশন', t: 'c' },
          { id: 'M02-territory', en: 'Territory Workload Balance', bn: 'টেরিটরি ব্যালেন্স', t: 'r' }
        ]
      }
    ],
    reports: ['Technician Utilization & Travel Time', 'First-Time Fix Rate by Skill', 'Geofence Breach & Delay Log', 'Field Payment Reconciliation'],
    forms: ['Create Field Work Order', 'Technician Dispatch Override', 'Emergency Reschedule Request'],
    cross: ['M01 Service Orders', 'M15 Truck-Stock Inventory', 'M21 Skill Matrix', 'M20 Mobile Invoicing'],
    freg: {
      src: 112,
      sub: [
        ['1', 'Automated Dispatch & Optimization', 12],
        ['2', 'Real-time GPS Tracking & ETA', 8],
        ['3', 'Mobile Work Order Execution', 10],
        ['4', 'Field Parts Consumption & Truck Stock', 9],
        ['5', 'Customer Signoff & Digital Evidence', 8],
        ['6', 'Field Payment & bKash / Cash Collection', 7]
      ]
    }
  },

  M31: {
    area: 'A02',
    code: 'M31',
    en: 'Workshop & Depot Repair',
    title: 'M31 · Workshop & Depot Repair',
    bn: 'ওয়ার্কশপ মেরামত',
    icon: '🔧',
    desc: 'Bench repair L1/L2/L3, serial genealogy, burn-in testing, workshop costing and knowledge capture.',
    kpis: [
      { l: 'Appointments Today' },
      { l: 'On-Time Arrival' },
      { l: 'On-Site Resolution' },
      { l: 'Customer Rating' }
    ],
    groups: [
      {
        en: 'Appointments',
        screens: [
          { id: 'M31-calendar', en: 'Appointment Scheduling Board', bn: 'অ্যাপয়েন্টমেন্ট বোর্ড', t: 'd' },
          { id: 'M31-all', en: 'On-Site Repair Requests', bn: 'অন-সাইট মেরামত অনুরোধ', t: 'g' },
          { id: 'M31-slots', en: 'Time-Slot Capacity Config', bn: 'স্লট ক্যাপাসিটি', t: 'g' }
        ]
      },
      {
        en: 'Execution & Safety',
        screens: [
          { id: 'M31-safety', en: 'Premises Safety Checklist', bn: 'নিরাপত্তা চেকলিস্ট', t: 'f' },
          { id: 'M31-triage', en: 'Pre-Visit Diagnostic Triage', bn: 'প্রি-ভিজিট ট্রায়াজ', t: 'g' },
          { id: 'M31-evidence', en: 'On-Site Photos & Signoff', bn: 'ডিজিটাল সাইনঅফ', t: 'f' }
        ]
      }
    ],
    reports: ['On-Site Resolution Rate', 'Customer Satisfaction by Zone', 'Parts Return Rate from Field'],
    forms: ['Book On-Site Service', 'Premises Safety Signoff', 'Escalation to Workshop Form'],
    cross: ['M01 Service Orders', 'M02 Dispatch Board', 'M15 Reserved Parts', 'M34 Customer Feedback'],
    freg: {
      src: 92,
      sub: [
        ['1', 'Appointment Booking & Slot Management', 10],
        ['2', 'Pre-Visit Triage & Tool Check', 8],
        ['3', 'Premises Inspection & Safety', 7],
        ['4', 'On-Site Repair & Calibration', 11],
        ['5', 'Digital Customer Signoff', 6]
      ]
    }
  },

  M03: {
    area: 'A02',
    code: 'M03',
    en: 'Service Logistics (Pick & Drop)',
    title: 'M03 · Service Logistics (Pick & Drop)',
    bn: 'সার্ভিস লজিস্টিক',
    icon: '📦',
    desc: 'Multi-leg consignments, unbroken chain of custody, POD with OTP, rider app, courier partners, COD.',
    kpis: [
      { l: 'Counter Intake Today' },
      { l: 'Avg Wait Time' },
      { l: 'Same-Day Fix Rate' },
      { l: '53 Hubs Online' }
    ],
    groups: [
      {
        en: 'Branch Front Desk',
        screens: [
          { id: 'M03-tokens', en: 'Live Queue & Token Board', bn: 'টোকেন কিউ বোর্ড', t: 'd' },
          { id: 'M03-intake', en: 'Branch Counter Intake', bn: 'কাউন্টার ইনটেক', t: 'f' },
          { id: 'M03-devices', en: 'Branch Custody Device Safe', bn: 'শাখা ডিভাইস নিরাপদ হেফাজত', t: 'g' }
        ]
      },
      {
        en: 'Workbench Operations',
        screens: [
          { id: 'M03-benches', en: 'Technician Workbench Allocations', bn: 'ওয়ার্কবেঞ্চ বরাদ্দ', t: 'g' },
          { id: 'M03-repair', en: 'Bench Diagnostic & Repair', bn: 'বেঞ্চ মেরামত', t: 'f' },
          { id: 'M03-ready', en: 'Ready for Collection Rack', bn: 'ডেলিভারি প্রস্তুত রেক', t: 'g' }
        ]
      }
    ],
    reports: ['Branch Daily Intake & Revenue', 'Bench Cycle Time by Model', 'Uncollected Customer Devices'],
    forms: ['Branch Walk-in Intake Form', 'Bench Transfer Form', 'Gate Pass & Handover Certificate'],
    cross: ['M01 Service Orders', 'M15 Branch Parts Store', 'M20 Cash Register & Mushak 6.3'],
    freg: {
      src: 104,
      sub: [
        ['1', 'Counter Token & Customer Intake', 12],
        ['2', 'Visual Condition Check & Photograph', 8],
        ['3', 'Bench Assignment & Work Queue', 9],
        ['4', 'Multi-Layer Soldering & Component Fix', 12],
        ['5', 'Counter Pickup & bKash Collection', 10]
      ]
    }
  },

  M04: {
    area: 'A02',
    code: 'M04',
    en: 'Branch & Front-Desk',
    title: 'M04 · Branch & Front-Desk',
    bn: 'শাখা ও ফ্রন্ট ডেস্ক',
    icon: '🏢',
    desc: 'Counter operations at 51+ centres — token queue, device custody, cash drawer, shift close, counter sales.',
    kpis: [
      { l: 'Parcels in Transit' },
      { l: 'On-Time Pickup' },
      { l: 'Chain-of-Custody Audits' }
    ],
    groups: [
      {
        en: 'Logistics Operations',
        screens: [
          { id: 'M04-manifests', en: 'Transfer Manifests & Bags', bn: 'ট্রান্সফার ম্যানিফেস্ট', t: 'g' },
          { id: 'M04-transit', en: 'Live District Hub Transit', bn: 'জেলা হাব ট্রানজিট', t: 'd' },
          { id: 'M04-couriers', en: 'Courier Partner Integration', bn: 'কুরিয়ার পার্টনার ইন্টিগ্রেশন', t: 'g' }
        ]
      }
    ],
    reports: ['Transit Damage & Loss Log', 'District Round-Trip TAT', 'Courier Delivery Success'],
    forms: ['Create Custody Bag Manifest', 'Seal Verification Check', 'Handover to Customer'],
    cross: ['M01 Service Orders', 'M03 Collection & Delivery', 'M47 Logistics Fleet'],
    freg: {
      src: 88,
      sub: [
        ['1', 'Tamper Bag Barcoding & Sealing', 10],
        ['2', 'Hub-to-Hub Routing & Waybill', 8],
        ['3', 'Third-Party Courier Handoff', 6],
        ['4', 'Safe Custody Delivery Verification', 8]
      ]
    }
  },

  M05: {
    area: 'A02',
    code: 'M05',
    en: 'Remote Support & MSP',
    title: 'M05 · Remote Support & MSP',
    bn: 'রিমোট সাপোর্ট ও এমএসপি',
    icon: '🖥️',
    desc: 'Managed IT services — remote sessions, monitored estate, alert-to-ticket, runbooks, patching, SLA credits.',
    kpis: [
      { l: 'Open Brand Claims' },
      { l: 'Claim Approval Rate' },
      { l: 'Reimbursement Pending' }
    ],
    groups: [
      {
        en: 'Claims Processing',
        screens: [
          { id: 'M05-claims', en: 'All Brand Claims', bn: 'সকল ওয়ারেন্টি দাবি', t: 'g' },
          { id: 'M05-claim-form', en: 'Brand Claim Record View', bn: 'দাবি ফর্ম', t: 'f' },
          { id: 'M05-oem-portal', en: 'OEM Portal Sync Status', bn: 'ওইএম পোর্টাল সিঙ্ক', t: 'c' }
        ]
      }
    ],
    reports: ['Claim Acceptance Rate by Brand', 'Defective Part Return Reconciliation', 'Reimbursement Settlement Ageing'],
    forms: ['File OEM Warranty Claim', 'DOA (Dead on Arrival) Certificate', 'Defective Part Return Notice'],
    cross: ['M01 Service Orders', 'M09 Entitlement Check', 'M15 OEM Parts Replacement', 'M20 Brand Invoicing'],
    freg: {
      src: 96,
      sub: [
        ['1', 'OEM API Warranty Entitlement Check', 12],
        ['2', 'Evidence Gathering & Photograph Upload', 8],
        ['3', 'Brand RMA Authorization', 10],
        ['4', 'Reimbursement Credit Note Settlement', 8]
      ]
    }
  },

  M06: {
    area: 'A02',
    code: 'M06',
    en: 'Data Services & Recovery',
    title: 'M06 · Data Services & Recovery',
    bn: 'ডেটা সেবা ও রিকভারি',
    icon: '💾',
    desc: 'Data recovery case management, sealed media custody, secure destruction with certificates, backup plans.',
    kpis: [
      { l: 'Active AMC Contracts' },
      { l: 'Covered Enterprise Seats' },
      { l: 'Preventive Visits MTD' }
    ],
    groups: [
      {
        en: 'Contracts & SLA',
        screens: [
          { id: 'M06-contracts', en: 'Corporate AMC Master List', bn: 'কর্পোরেট এএমসি তালিকা', t: 'g' },
          { id: 'M06-contract-view', en: 'AMC Contract Record View', bn: 'এএমসি চুক্তি নথি', t: 'f' },
          { id: 'M06-pm-planner', en: 'Preventive Maintenance Planner', bn: 'পিএম সিডিউল', t: 'd' }
        ]
      }
    ],
    reports: ['Enterprise SLA Compliance Scorecard', 'AMC Revenue & Renewal Projections', 'Preventive Maintenance Completion'],
    forms: ['Create Corporate AMC Agreement', 'Add Asset Estate to AMC', 'Quarterly Service Audit Signoff'],
    cross: ['M36 B2B Accounts', 'M02 Dedicated Tech Dispatch', 'M19 Deferred Revenue Billing'],
    freg: {
      src: 110,
      sub: [
        ['1', 'Multi-Site Contract Pricing & SLAs', 14],
        ['2', 'Preventive Maintenance Scheduling', 10],
        ['3', 'Corporate Equipment Inventory Registration', 9],
        ['4', 'Priority Dispatch Queue Rules', 8]
      ]
    }
  },

  /* ============ A03 · CUSTOMER EXPERIENCE ============================= */
  M33: {
    area: 'A03', code: 'M33', en: 'Customer & Party Master', title: 'M33 · Customer & Party Master',
    bn: 'গ্রাহক মাস্টার', icon: '🪪',
    desc: 'Single golden record for every party — roles, hierarchies, OTP verification, consent, segments, credit.',
    kpis: [
      { l: 'Self-Bookings Today' },
      { l: 'Online Estimate Approval' },
      { l: 'bKash Self-Pay Share' }
    ],
    groups: [
      {
        en: 'Portal Engagement',
        screens: [
          { id: 'M33-bookings', en: 'Online Customer Bookings', bn: 'অনলাইন বুকিং', t: 'g' },
          { id: 'M33-tracker', en: 'Real-time Tracking Simulator', bn: 'ট্র্যাকিং সিমুলেটর', t: 'd' }
        ]
      }
    ],
    reports: ['Portal Drop-off Funnel', 'Customer Self-Service Adoption', 'Digital Payment Breakdown'],
    forms: ['Public Booking Test Form'],
    cross: ['M01 Service Orders', 'M35 Customer Self-Payment', 'P01 Public Web Portal'],
    freg: { src: 84, sub: [['1', 'Online Booking Wizard', 12], ['2', 'OTP Customer Authentication', 8], ['3', 'bKash / Nagad Instant Pay', 10]] }
  },

  M07: {
    area: 'A03', code: 'M07', en: 'CRM & Sales Pipeline', title: 'M07 · CRM & Sales Pipeline',
    bn: 'সিআরএম ও বিক্রয়', icon: '🎯',
    desc: 'Leads, opportunities, corporate account plans, QBRs, renewals T-90, cross-sell and win/loss.',
    kpis: [
      { l: 'Active Customer Accounts' },
      { l: 'Repeat Customer Rate' },
      { l: 'Avg Customer Rating' }
    ],
    groups: [
      {
        en: 'Profiles & History',
        screens: [
          { id: 'M07-customers', en: 'Unified Customer Directory', bn: 'কাস্টমার ডিরেক্টরি', t: 'g' },
          { id: 'M07-360', en: 'Customer 360 Degree View', bn: 'কাস্টমার ৩৬০ ভিউ', t: 'x' }
        ]
      }
    ],
    reports: ['Customer Lifetime Value', 'Device Repair Frequency', 'Customer Retention Analysis'],
    forms: ['Create Customer Profile', 'Merge Duplicate Accounts'],
    cross: ['M01 Service Orders', 'M17 Device Registry', 'M34 Customer Feedback'],
    freg: { src: 90, sub: [['1', 'Master Identity Resolution', 10], ['2', 'Customer Lifetime Audit', 8], ['3', 'Communication History', 9]] }
  },

  M10: {
    area: 'A03', code: 'M10', en: 'Loyalty & Rewards', title: 'M10 · Loyalty & Rewards',
    bn: 'লয়্যালটি ও পুরস্কার', icon: '🎁',
    desc: 'Privilege tiers, points ledger, wallet, vouchers, referral programme, alliance benefits, liability.',
    kpis: [
      { l: 'Calls Handled Today' },
      { l: 'Average Handle Time' },
      { l: 'First-Contact Resolution' }
    ],
    groups: [
      {
        en: 'Contact Queues',
        screens: [
          { id: 'M10-telephony', en: 'Hotline 16743 Agent Console', bn: 'হটলাইন এজেন্ট কনসোল', t: 'c' },
          { id: 'M10-whatsapp', en: 'WhatsApp & Chat Tickets', bn: 'হোয়াটসঅ্যাপ চ্যাট টিকেট', t: 'g' }
        ]
      }
    ],
    reports: ['Call Volume & Abandonment Rate', 'Agent Performance Scorecard', 'Bengali Sentiment Score'],
    forms: ['Log Call Ticket', 'Escalate to Service Order'],
    cross: ['M01 Intake Queue', 'M07 Customer Profile'],
    freg: { src: 98, sub: [['1', 'CTI Telephony Integration', 12], ['2', 'WhatsApp AI Conversational Agent', 14], ['3', 'Omnichannel Ticket Routing', 10]] }
  },

  M34: {
    area: 'A03', code: 'M34', en: 'CX, Feedback & Complaints', title: 'M34 · CX, Feedback & Complaints',
    bn: 'অভিজ্ঞতা ও অভিযোগ', icon: '💬',
    desc: 'CSAT/NPS/CES surveys, closed feedback loop, complaint SLA & escalation, goodwill authority, VoC analytics.',
    kpis: [
      { l: 'CSAT Score' },
      { l: 'NPS Net Score' },
      { l: 'Survey Response Rate' }
    ],
    groups: [
      {
        en: 'Feedback Stream',
        screens: [
          { id: 'M34-responses', en: 'Customer Survey Responses', bn: 'কাস্টমার সার্ভে রেসপন্স', t: 'g' },
          { id: 'M34-detractors', en: 'Detractor Resolution Queue', bn: 'ডিট্র্যাক্টর রিজোলিউশন', t: 'g' }
        ]
      }
    ],
    reports: ['CSAT Trend by Service Branch', 'Technician Service Quality Ranking', 'NPS Root-Cause Distribution'],
    forms: ['Log Customer Detractor Call'],
    cross: ['M01 Service Order', 'M02 Technician Roster', 'M23 ISO 9001 Quality'],
    freg: { src: 76, sub: [['1', 'Post-Service Automated Survey', 8], ['2', 'Real-time Detractor Alerting', 6], ['3', 'NPS Analytics Engine', 8]] }
  },

  M27: {
    area: 'A03', code: 'M27', en: 'Contact Centre (16743)', title: 'M27 · Contact Centre (16743)',
    bn: 'কল সেন্টার ১৬৭৪৩', icon: '🎧',
    desc: 'Unified voice + digital conversations, skills routing, agent desktop with Customer-360 pop, notifications for the ERP.',
    kpis: [
      { l: 'Overall SLA Compliance' },
      { l: 'Breaches This Month' }
    ],
    groups: [
      {
        en: 'SLA Engine',
        screens: [
          { id: 'M27-policies', en: 'Configured SLA Policies', bn: 'এসএলএ পলিসি কনফিগারেশন', t: 'g' },
          { id: 'M27-breaches', en: 'Active SLA Breach Warnings', bn: 'সক্রিয় এসএলএ লঙ্ঘন সতর্কতা', t: 'g' }
        ]
      }
    ],
    reports: ['SLA Compliance by Branch', 'Hold-Time Impact Analysis'],
    forms: ['Create SLA Policy Rule'],
    cross: ['M01 Order Life-Cycle', 'M02 Field Dispatch'],
    freg: { src: 72, sub: [['1', 'Multi-Tier Policy Definition', 8], ['2', 'Working-Hour Calendar Engine', 8], ['3', 'Auto-Escalation Engine', 9]] }
  },

  M32: {
    area: 'A03', code: 'M32', en: 'Conversational AI (Bengali)', title: 'M32 · Conversational AI (Bengali)',
    bn: 'কথোপকথন এআই', icon: '🤖',
    desc: 'Bengali-first assistant — intent recognition, RAG on live ERP data, authenticated actions, human handoff.',
    kpis: [
      { l: 'Operational Branches' },
      { l: 'Cash Reconciled Today' }
    ],
    groups: [
      {
        en: 'Branch Control',
        screens: [
          { id: 'M32-branches', en: 'All 53 Service Branches Directory', bn: '৫৩টি সার্ভিস শাখা তালিকা', t: 'g' },
          { id: 'M32-shifts', en: 'Branch Shift & Staffing Rosters', bn: 'শিফট ও স্টাফিং রোস্টার', t: 'g' }
        ]
      }
    ],
    reports: ['Branch Performance Benchmark', 'Cash Drawer Variance Log'],
    forms: ['Branch Opening/Closing Checklist'],
    cross: ['M03 Walk-In Repairs', 'M19 Daily Cash Reconciliation'],
    freg: { src: 80, sub: [['1', '53-Hub Master Directory', 10], ['2', 'Daily Branch Cash Closing', 8], ['3', 'Shift Management', 8]] }
  },

  M35: {
    area: 'A03', code: 'M35', en: 'Marketing Campaigns', title: 'M35 · Marketing Campaigns',
    bn: 'মার্কেটিং ক্যাম্পেইন', icon: '📣',
    desc: 'Segment-driven journeys, offer selection, A/B & attribution, seasonal templates, co-marketing with partners.',
    kpis: [
      { l: 'Online Payments Today' },
      { l: 'bKash Success Rate' }
    ],
    groups: [
      {
        en: 'Payment Gateway',
        screens: [
          { id: 'M35-transactions', en: 'Online Customer Transactions', bn: 'অনলাইন লেনদেন', t: 'g' },
          { id: 'M35-links', en: 'Instant Payment Links Generated', bn: 'পেমেন্ট লিংক', t: 'g' }
        ]
      }
    ],
    reports: ['Payment Gateway Settlement Log', 'Failed Payment Analysis'],
    forms: ['Generate Custom Payment Link'],
    cross: ['M20 Mushak 6.3 Invoicing', 'M01 Service Orders'],
    freg: { src: 78, sub: [['1', 'bKash Merchant Checkout Integration', 10], ['2', 'Nagad & Card Processing', 10], ['3', 'Automated SMS Receipt Issuance', 8]] }
  },

  /* ============ A04 · COMMERCIAL & REVENUE ============================= */
  M37: {
    area: 'A04', code: 'M37', en: 'Product & Service Catalogue', title: 'M37 · Product & Service Catalogue',
    bn: 'পণ্য ও সেবা ক্যাটালগ', icon: '🧾',
    desc: 'Everything sellable — unified item master, rBOM, standard repair time, fault taxonomy, 14 contract families.',
    kpis: [
      { l: 'Active Catalog SKUs' },
      { l: 'rBOM Coverage' }
    ],
    groups: [
      {
        en: 'Catalogue Masters',
        screens: [
          { id: 'M37-items', en: 'Unified Item Master', bn: 'ইউনিফাইড আইটেম মাস্টার', t: 'g' },
          { id: 'M37-services', en: 'Service Definitions & SRT', bn: 'সার্ভিস ও স্ট্যান্ডার্ড সময়', t: 'g' }
        ]
      }
    ],
    reports: ['Catalog Coverage by Brand', 'Item Margin Analysis'],
    forms: ['Create Catalogue Item', 'Define Repair BOM (rBOM)'],
    cross: ['M11 Pricing & Rate Cards', 'M15 Spare Parts Inventory'],
    freg: { src: 120, sub: [['1', 'Unified Item Master', 14], ['2', 'Repair BOM (rBOM) Engine', 12], ['3', 'Standard Repair Time (SRT)', 10]] }
  },

  M11: {
    area: 'A04', code: 'M11', en: 'Pricing & Rate Cards', title: 'M11 · Pricing & Rate Cards',
    bn: 'মূল্য ও রেট কার্ড', icon: '🏷️',
    desc: 'Price engine (item×customer×channel×date), labour rate cards, brand reimbursement rates, discount governance.',
    kpis: [{ l: 'Realised Margin' }, { l: 'Active Rate Cards' }],
    groups: [
      { en: 'Pricing Engines', screens: [{ id: 'M11-cards', en: 'Standard Labor Rate Cards', bn: 'লেবার রেট কার্ড', t: 'g' }] }
    ],
    reports: ['Margin Floor Exception Log'], forms: ['Create Labor Rate Card'], cross: ['M37 Catalogue', 'M01 Estimates'],
    freg: { src: 88, sub: [['1', 'Labor Rate Matrix Engine', 10], ['2', 'Discount Threshold Rules', 8]] }
  },

  M36: {
    area: 'A04', code: 'M36', en: 'Quotations & Tenders', title: 'M36 · Quotations & Tenders',
    bn: 'কোটেশন ও টেন্ডার', icon: '📄',
    desc: 'Estimate build-up to customer quotation, multi-channel approval loop, e-signature, tender & competitive bids.',
    kpis: [{ l: 'Active B2B Clients' }, { l: 'Total B2B Billing MTD' }],
    groups: [
      { en: 'Accounts', screens: [{ id: 'M36-accounts', en: 'B2B Client Directory', bn: 'বি২বি ক্লায়েন্ট ডিরেক্টরি', t: 'g' }] }
    ],
    reports: ['Corporate Client Revenue Share'], forms: ['New B2B Account Onboarding'], cross: ['M06 Corporate AMC', 'M19 Accounts Receivable'],
    freg: { src: 94, sub: [['1', 'Corporate Account Master', 12], ['2', 'Credit Limit & Terms Config', 8]] }
  },

  M08: {
    area: 'A04', code: 'M08', en: 'Contract Lifecycle (AMC)', title: 'M08 · Contract Lifecycle (AMC)',
    bn: 'চুক্তি ব্যবস্থাপনা', icon: '📑',
    desc: '14 contract families — entitlement definition/consumption, PM schedules, SLA credits, amendments, renewals.',
    kpis: [{ l: 'Active Tenders' }, { l: 'Contract Win Rate' }],
    groups: [
      { en: 'Tenders', screens: [{ id: 'M08-tenders', en: 'Tenders & Contracts List', bn: 'চুক্তি ও টেন্ডার তালিকা', t: 'g' }] }
    ],
    reports: ['Tender Pipeline Value'], forms: ['Register New Tender'], cross: ['M36 B2B Accounts'],
    freg: { src: 82, sub: [['1', 'Tender Opportunity Tracking', 10], ['2', 'Bank Guarantee Management', 8]] }
  },

  M09: {
    area: 'A04', code: 'M09', en: 'Warranty & Claims', title: 'M09 · Warranty & Claims',
    bn: 'ওয়ারেন্টি ও ক্লেইম', icon: '🛡️',
    desc: 'Warranty register, entitlement "who pays", brand claims with auto evidence packs, recalls, protection plans.',
    kpis: [{ l: 'Lookups Today' }, { l: 'Instant Match Rate' }],
    groups: [
      { en: 'Entitlement', screens: [{ id: 'M09-lookup', en: 'Serial Number Entitlement Lookup', bn: 'সিরিয়াল অনুসন্ধান', t: 'g' }] }
    ],
    reports: ['Warranty Expiry Forecast'], forms: ['Verify Device Warranty Form'], cross: ['M01 Intake', 'M05 Brand Claims'],
    freg: { src: 76, sub: [['1', 'OEM API Live Entitlement Hook', 12], ['2', 'Physical Damage & Void Check', 8]] }
  },

  M39: {
    area: 'A04', code: 'M39', en: 'Subscriptions & Recurring', title: 'M39 · Subscriptions & Recurring',
    bn: 'সাবস্ক্রিপশন', icon: '🔄',
    desc: 'Zuora-class billing — schedules, usage rating, proration, dunning, MRR/ARR/churn/NRR metrics.',
    kpis: [{ l: 'Billed This Cycle' }],
    groups: [
      { en: 'Billing Engine', screens: [{ id: 'M39-cycles', en: 'AMC Recurring Billing Schedules', bn: 'রিকারিং বিলিং শিডিউল', t: 'g' }] }
    ],
    reports: ['Recurring Billing Projections'], forms: ['Generate AMC Billing Cycle'], cross: ['M06 AMC', 'M20 Invoicing'],
    freg: { src: 74, sub: [['1', 'Automated Cycle Generator', 10], ['2', 'Advance Revenue Deferral', 8]] }
  },

  M38: {
    area: 'A04', code: 'M38', en: 'E-Commerce Storefront', title: 'M38 · E-Commerce Storefront',
    bn: 'ই-কমার্স', icon: '🛒',
    desc: 'Online storefront — compatibility filtering, mixed carts, service booking as commerce, bKash/Nagad/card checkout.',
    kpis: [{ l: 'Leakage Rate' }, { l: 'Audits Run Today' }],
    groups: [
      { en: 'Audit Engine', screens: [{ id: 'M38-audits', en: 'Job-to-Bill Reconciliation Audit', bn: 'বিলিং অডিট রিপোর্ট', t: 'g' }] }
    ],
    reports: ['Unbilled Parts Discrepancy Log'], forms: ['Flag Revenue Leakage'], cross: ['M01 Service Orders', 'M20 Invoicing'],
    freg: { src: 80, sub: [['1', 'Discrepancy Detection Algorithm', 12], ['2', 'Unbilled WIP Reconciler', 10]] }
  },

  M12: {
    area: 'A04', code: 'M12', en: 'Marketplace & Sellers', title: 'M12 · Marketplace & Sellers',
    bn: 'মার্কেটপ্লেস', icon: '🌐',
    desc: 'Freelance engineer / shop ecosystem — KYC, listings, job broadcast & bidding, commission, wallets, disputes.',
    kpis: [{ l: 'Active Price Books' }],
    groups: [
      { en: 'Price Books', screens: [{ id: 'M12-books', en: 'Price Books Matrix', bn: 'প্রাইস বুক তালিকা', t: 'g' }] }
    ],
    reports: ['Price Update History'], forms: ['Create New Price Book'], cross: ['M37 Catalogue', 'M11 Pricing'],
    freg: { src: 70, sub: [['1', 'Multi-Tier Price Book Editor', 10], ['2', 'Effective Date Scheduling', 8]] }
  },

  M40: {
    area: 'A04', code: 'M40', en: 'Partner & Channel', title: 'M40 · Partner & Channel',
    bn: 'পার্টনার ও চ্যানেল', icon: '🤝',
    desc: 'Brand partnerships (17+), alliances, referral partners, deal registration, resellers, franchise management.',
    kpis: [{ l: 'Channel Partners' }],
    groups: [
      { en: 'Channel Margins', screens: [{ id: 'M40-margins', en: 'Partner Margin Schedules', bn: 'পার্টনার মার্জিন', t: 'g' }] }
    ],
    reports: ['Channel Commission Settlement'], forms: ['Approve Channel Commission'], cross: ['M36 Corporate Accounts'],
    freg: { src: 68, sub: [['1', 'Commission Calculation Rules', 8], ['2', 'Partner Payout Generator', 8]] }
  },

  /* ============ A05 · CIRCULAR ECONOMY ================================ */
  M13: {
    area: 'A05', code: 'M13', en: 'Rental & EaaS', title: 'M13 · Rental & EaaS',
    bn: 'ভাড়া ও ইকুইপমেন্ট', icon: '🎥',
    desc: '8 asset categories — fleet register, availability, agreements & deposits, damage recovery, utilisation.',
    kpis: [{ l: 'E-Waste Recycled MTD' }],
    groups: [
      { en: 'Recycling', screens: [{ id: 'M13-intake', en: 'E-Waste Intake Registry', bn: 'ই-বর্জ্য ইনটেক রেজিস্ট্রি', t: 'g' }] }
    ],
    reports: ['RoHS Environmental Compliance Certificate'], forms: ['Log E-Waste Intake Form'], cross: ['M14 Refurbishment'],
    freg: { src: 84, sub: [['1', 'Weighing & Hazardous Materials Log', 10], ['2', 'Certified Destruction Certificate', 8]] }
  },

  M14: {
    area: 'A05', code: 'M14', en: 'Trade-In & Refurbishment', title: 'M14 · Trade-In & Refurbishment',
    bn: 'ট্রেড-ইন ও রিফার্বিশ', icon: '♻️',
    desc: 'Automated valuation, provenance screening, refurb work orders, A-D grading, harvest-to-parts, resale.',
    kpis: [{ l: 'Devices Refurbished MTD' }, { l: 'Avg Resale Margin' }],
    groups: [
      { en: 'Refurbishment', screens: [{ id: 'M14-grading', en: 'Refurbishment Grading Station', bn: 'রিফার্বিশমেন্ট গ্রেডিং', t: 'g' }] }
    ],
    reports: ['Refurbished Devices Yield'], forms: ['Device Condition Grade Sheet'], cross: ['M17 Device Registry', 'M15 Parts'],
    freg: { src: 92, sub: [['1', 'Condition Grading Algorithm', 10], ['2', 'Testing & Repackaging Station', 12]] }
  },

  M18: {
    area: 'A05', code: 'M18', en: 'E-Waste & Recycling', title: 'M18 · E-Waste & Recycling',
    bn: 'ই-বর্জ্য ও রিসাইক্লিং', icon: '🌱',
    desc: 'Collection network, triage & disposition, certified partners, statutory DoE/BTRC returns, impact reporting.',
    kpis: [{ l: 'Salvaged Components Value' }],
    groups: [
      { en: 'Scrap', screens: [{ id: 'M18-salvage', en: 'Harvested Parts Salvage Store', bn: 'উদ্ধারকৃত পার্টস তালিকা', t: 'g' }] }
    ],
    reports: ['Scrap Auction & Revenue Log'], forms: ['Component Harvesting Request'], cross: ['M15 Inventory'],
    freg: { src: 68, sub: [['1', 'Component Salvage Certification', 8], ['2', 'Scrap Auction Tender', 8]] }
  },

  /* ============ A06 · SUPPLY CHAIN ==================================== */
  M15: {
    area: 'A06', code: 'M15', en: 'Spare Parts & Inventory', title: 'M15 · Spare Parts & Inventory',
    bn: 'স্পেয়ার পার্টস ও ইনভেন্টরি', icon: '🧰',
    desc: 'Stock ledger across 6 ownership classes — serial/lot trace, van stock, valuation, transfers, counts.',
    kpis: [{ l: 'Inventory Accuracy' }, { l: 'Stock Value' }, { l: 'Part Availability' }, { l: 'Dead Stock' },
           { l: 'Van Variance' }, { l: 'Turns (annualised)' }],
    groups: [
      { en: 'Stock Ledger', screens: [
        { id: 'M15-onhand', en: 'On-Hand by Location', bn: 'স্টক লেজার', t: 'g' },
        { id: 'M15-ownership', en: '6 Ownership Classes', bn: 'মালিকানা শ্রেণি', t: 'g' },
        { id: 'M15-movements', en: 'Issues & Returns', bn: 'ইস্যু ও ফেরত', t: 'g' },
        { id: 'M15-network', en: 'Network Availability Search', bn: 'নেটওয়ার্ক অনুসন্ধান', t: 'c' }] },
      { en: 'Traceability', screens: [
        { id: 'M15-serials', en: 'Serial & Lot Trace', bn: 'সিরিয়াল ট্রেস', t: 'g' },
        { id: 'M15-genealogy', en: 'Consumption Genealogy', bn: 'ব্যবহার বংশতালিকা', t: 'r' }] },
      { en: 'Van Stock', screens: [
        { id: 'M15-van', en: 'Van Stock by Technician', bn: 'ভ্যান স্টক', t: 'g' },
        { id: 'M15-replen', en: 'Replenishment & Par', bn: 'পূরণকরণ', t: 'g' },
        { id: 'M15-recon', en: 'Daily Reconciliation', bn: 'দৈনিক মিলকরণ', t: 'c' }] },
      { en: 'Control', screens: [
        { id: 'M15-counts', en: 'Cycle & Full Counts', bn: 'গণনা', t: 'c' },
        { id: 'M15-transfers', en: 'Inter-Branch Transfers', bn: 'শাখা স্থানান্তর', t: 'g' },
        { id: 'M15-quarantine', en: 'Quarantine & Scrap', bn: 'কোয়ারেন্টাইন', t: 'g' },
        { id: 'M15-rtv', en: 'RTV Initiation', bn: 'ফেরত প্রেরণ', t: 'g' }] },
      { en: 'Valuation & Analysis', screens: [
        { id: 'M15-valuation', en: 'Valuation (FIFO/WAC)', bn: 'মূল্যায়ন', t: 'r' },
        { id: 'M15-ageing', en: 'Ageing & Obsolescence', bn: 'বয়স ও অবচয়', t: 'r' },
        { id: 'M15-abc', en: 'ABC / XYZ / Criticality', bn: 'এবিসি বিশ্লেষণ', t: 'r' }] }
    ],
    reports: ['Stock Valuation by Class', 'Inventory Accuracy Audit', 'Ageing & Dead Stock',
              'Van Stock Variance', 'Transfer Performance', 'ABC Segmentation'],
    // Data-entry forms = capture labels (sub-module order), then registry forms
    // with no backing model yet (each listed under `gaps`).
    forms: ['Spare Part', 'Stock Location', 'Stock Issue', 'Van Stock Location', 'Reorder Rule',
            'Valuation Entry', 'Part Segment Classification', 'Transfer Request',
            'Return-to-Vendor Consignment', 'Goods Receipt (inspection gate)', 'Cycle Count', 'Scrap Order'],
    cross: ['M41 warehouse execution', 'M16 procurement', 'M02 van consumption', 'M09 consignment stock',
            'M31 bench stock'],
    freg: { src: 107, sub: [
      ['1', 'On-Hand & Classes', 12], ['2', 'Location Hierarchy', 8], ['3', 'Ownership Segregation', 9],
      ['4', 'Reservations', 7], ['5', 'Issue / Return / Consumption', 10], ['6', 'Van Stock', 11],
      ['7', 'Serial & Lot Trace', 10], ['8', 'Valuation', 8], ['9', 'Goods Receipt', 7], ['10', 'Counting', 9],
      ['11', 'Ageing & Analysis', 8], ['12', 'Transfers & RTV', 8]] },
    // Capture map (CD-M15, A06 audit): cd_inventory, cd_consignment, cd_demand_plan.
    // Every sub-module (freg) and screen opens the real Odoo form it captures into.
    captures: [
      { en: 'Spare Part', bn: 'স্পেয়ার পার্ট', model: 'fix.spare.part', freg: ['1'], screens: ['M15-onhand'] },
      { en: 'Stock Location', bn: 'স্টক লোকেশন', model: 'fix.stock.location', freg: ['2'], screens: ['M15-onhand'] },
      { en: 'Stock Issue', bn: 'স্টক ইস্যু', model: 'fix.stock.consumption', freg: ['5'], screens: ['M15-movements'] },
      { en: 'Van Stock Location', bn: 'ভ্যান স্টক লোকেশন', model: 'fix.stock.location', ctx: { default_location_type: 'van' }, freg: ['6'], screens: ['M15-van'] },
      { en: 'Reorder Rule', bn: 'পুনঃঅর্ডার নিয়ম', model: 'fix.reorder.rule', freg: ['6'], screens: ['M15-replen'] },
      { en: 'Valuation Entry', bn: 'মূল্যায়ন এন্ট্রি', model: 'fix.inventory.valuation.suspense', ctx: { default_entry_type: 'revaluation' }, freg: ['8'], screens: ['M15-valuation'] },
      { en: 'Part Segment Classification', bn: 'পার্টস সেগমেন্ট শ্রেণীকরণ', model: 'fix.part.segment', freg: ['11'], screens: ['M15-abc'] },
      { en: 'Transfer Request', bn: 'স্থানান্তর অনুরোধ', model: 'fix.consignment', ctx: { default_consignment_type: 'branch_transfer' }, freg: ['12'], screens: ['M15-transfers'] },
      { en: 'Return-to-Vendor Consignment', bn: 'সরবরাহকারীকে ফেরত চালান', model: 'fix.consignment', ctx: { default_consignment_type: 'return_to_vendor' }, freg: ['12'], screens: ['M15-rtv'] }
    ],
    // Gaps: no backing model in addons/ yet. Their buttons say so instead of
    // opening an unrelated form.
    gaps: [
      { en: 'Ownership Class Assignment', freg: ['3'], screens: ['M15-ownership'], note: 'no ownership-class field or record (6 classes) on any stock model' },
      { en: 'Stock Reservation', freg: ['4'], screens: [], note: 'only a qty_reserved counter on fix.spare.part; no reservation record' },
      { en: 'Serial / Lot Record', freg: ['7'], screens: ['M15-serials', 'M15-genealogy'], note: 'no serial/lot model; a serial is free text on fix.stock.consumption' },
      { en: 'Goods Receipt (inspection gate)', freg: ['9'], screens: [], note: 'no GRN model; receipt is only qty_received on fix.purchase.order.line' },
      { en: 'Cycle Count', freg: ['10'], screens: ['M15-counts'], note: 'no count plan / count sheet model' },
      { en: 'Network Availability Search', freg: [], screens: ['M15-network'], note: 'search console over on-hand stock; no record to capture' },
      { en: 'Van Reconciliation', freg: [], screens: ['M15-recon'], note: 'no daily van reconciliation record' },
      { en: 'Scrap Order', freg: [], screens: ['M15-quarantine'], note: 'no quarantine disposition / scrap order model' },
      { en: 'Ageing & Obsolescence Review', freg: [], screens: ['M15-ageing'], note: 'no ageing or obsolescence provision model' }
    ]
  },

  M41: {
    area: 'A06', code: 'M41', en: 'Warehouse Management', title: 'M41 · Warehouse Management',
    bn: 'ওয়্যারহাউস ব্যবস্থাপনা', icon: '🏭',
    desc: 'Physical execution — bins & slots, directed put-away, wave picking, packing, RF mobile, task interleaving.',
    kpis: [{ l: 'Pick Accuracy' }, { l: 'Lines Picked Today' }, { l: 'Waves Open' },
           { l: 'Dock Appointments' }, { l: 'Labour Efficiency' }, { l: 'Short-Picks' }],
    groups: [
      { en: 'Structure', screens: [
        { id: 'M41-zones', en: 'Zones, Aisles & Bins', bn: 'জোন ও বিন', t: 'g' },
        { id: 'M41-slotting', en: 'Slotting & Re-Slotting', bn: 'স্লটিং', t: 'g' }] },
      { en: 'Inbound', screens: [
        { id: 'M41-docks', en: 'Dock Appointments', bn: 'ডক অ্যাপয়েন্টমেন্ট', t: 'g' },
        { id: 'M41-receiving', en: 'Scan Receiving', bn: 'রিসিভিং', t: 'c' },
        { id: 'M41-putaway', en: 'Directed Put-Away', bn: 'পুট-অ্যাওয়ে', t: 'g' }] },
      { en: 'Outbound', screens: [
        { id: 'M41-waves', en: 'Wave Planning', bn: 'ওয়েভ পরিকল্পনা', t: 'c' },
        { id: 'M41-picking', en: 'Pick Strategies', bn: 'পিকিং', t: 'g' },
        { id: 'M41-packing', en: 'Packing & Cartons', bn: 'প্যাকিং', t: 'g' },
        { id: 'M41-staging', en: 'Staging & Load', bn: 'স্টেজিং', t: 'g' }] },
      { en: 'Floor Ops', screens: [
        { id: 'M41-rf', en: 'RF Mobile App', bn: 'আরএফ অ্যাপ', t: 'd' },
        { id: 'M41-tasks', en: 'Task Management', bn: 'কাজ ব্যবস্থাপনা', t: 'g' },
        { id: 'M41-counting', en: 'Floor Counts', bn: 'ফ্লোর গণনা', t: 'g' }] }
    ],
    reports: ['Throughput by Shift', 'Pick Accuracy Trend', 'Wave Cycle Time', 'Labour Productivity',
              'Bin Utilisation Heatmap'],
    // Data-entry forms = capture labels (sub-module order), then registry forms
    // with no backing model yet (each listed under `gaps`).
    forms: ['Warehouse', 'Warehouse Zone', 'Bin', 'Wave Template', 'Dock Appointment',
            'Packing Station Config'],
    cross: ['M15 stock ledger', 'M16 goods receipt', 'M03 outbound staging', 'M44 import receiving'],
    freg: { src: 78, sub: [
      ['1', 'Physical Structure', 8], ['2', 'Slotting', 7], ['3', 'Inbound & Put-Away', 12],
      ['4', 'Wave Planning', 9], ['5', 'Picking', 11], ['6', 'Packing & Staging', 8],
      ['7', 'Replenishment', 6], ['8', 'RF Execution', 8], ['9', 'Labour & Analytics', 9]] },
    // Capture map (CD-M41, A06 audit): cd_wms_structure. Execution sub-modules have no backend yet.
    // Every sub-module (freg) and screen opens the real Odoo form it captures into.
    captures: [
      { en: 'Warehouse', bn: 'গুদাম', model: 'fix.warehouse', freg: ['1'], screens: ['M41-zones'] },
      { en: 'Warehouse Zone', bn: 'গুদাম জোন', model: 'fix.warehouse.zone', freg: ['1'], screens: ['M41-zones'] },
      { en: 'Bin', bn: 'বিন', model: 'fix.warehouse.bin', freg: ['1'], screens: ['M41-zones'] }
    ],
    // Gaps: no backing model in addons/ yet. Their buttons say so instead of
    // opening an unrelated form.
    gaps: [
      { en: 'Slotting Rule', freg: ['2'], screens: ['M41-slotting'], note: 'no slotting / pick-face model' },
      { en: 'Dock Appointment', freg: ['3'], screens: ['M41-docks'], note: 'no dock door or appointment model' },
      { en: 'Scan Receipt & Put-Away Task', freg: ['3'], screens: ['M41-receiving', 'M41-putaway'], note: 'no inbound receipt or put-away task model' },
      { en: 'Wave Template', freg: ['4'], screens: ['M41-waves'], note: 'no wave or wave template model' },
      { en: 'Pick Task', freg: ['5'], screens: ['M41-picking'], note: 'no pick list / pick task model' },
      { en: 'Packing Station Config', freg: ['6'], screens: ['M41-packing', 'M41-staging'], note: 'no packing station, carton or staging model' },
      { en: 'Bin Replenishment Task', freg: ['7'], screens: [], note: 'no pick-face replenishment model (fix.reorder.rule is supplier reorder, M15)' },
      { en: 'RF Task', freg: ['8'], screens: ['M41-rf', 'M41-tasks'], note: 'no RF session or warehouse task model' },
      { en: 'Labour Standard', freg: ['9'], screens: [], note: 'no time standard or productivity model' },
      { en: 'Floor Count', freg: [], screens: ['M41-counting'], note: 'no count plan / count sheet model' }
    ]
  },

  M16: {
    area: 'A06', code: 'M16', en: 'Procurement & Sourcing', title: 'M16 · Procurement & Sourcing',
    bn: 'ক্রয় ও সোর্সিং', icon: '🛍️',
    desc: 'Demand-to-PO, RFQ with normalised comparison, three-way match, blanket orders, expediting, spend analysis.',
    kpis: [{ l: 'Open PRs' }, { l: 'POs Awaiting Approval' }, { l: '3-Way Match Exceptions' },
           { l: 'Vendor OTD' }, { l: 'Spend Under Contract' }, { l: 'Emergency Purchases' }],
    groups: [
      { en: 'Requisitions', screens: [
        { id: 'M16-prs', en: 'Purchase Requisitions', bn: 'ক্রয় অনুরোধ', t: 'g' },
        { id: 'M16-consol', en: 'Cross-Branch Consolidation', bn: 'একত্রীকরণ', t: 'c' }] },
      { en: 'Sourcing', screens: [
        { id: 'M16-rfqs', en: 'RFQ Events', bn: 'আরএফকিউ', t: 'g' },
        { id: 'M16-compare', en: 'Bid Comparison', bn: 'দর তুলনা', t: 'f' },
        { id: 'M16-award', en: 'Award Decisions', bn: 'পুরস্কার সিদ্ধান্ত', t: 'g' }] },
      { en: 'Orders', screens: [
        { id: 'M16-pos', en: 'Purchase Orders', bn: 'ক্রয় আদেশ', t: 'g' },
        { id: 'M16-blanket', en: 'Blanket / Call-Off', bn: 'ব্ল্যাঙ্কেট আদেশ', t: 'g' },
        { id: 'M16-expedite', en: 'Expediting Desk', bn: 'ত্বরান্বিতকরণ', t: 'c' }] },
      { en: 'Receiving & Match', screens: [
        { id: 'M16-grn', en: 'Goods Receipts', bn: 'পণ্য গ্রহণ', t: 'g' },
        { id: 'M16-inspection', en: 'Inspection Outcomes', bn: 'পরিদর্শন', t: 'g' },
        { id: 'M16-match', en: '3-Way Match Workbench', bn: 'ত্রিমুখী মিলকরণ', t: 'c' }] },
      { en: 'Analysis', screens: [
        { id: 'M16-spend', en: 'Spend Analysis', bn: 'ব্যয় বিশ্লেষণ', t: 'r' },
        { id: 'M16-pricehist', en: 'Price History & Alerts', bn: 'মূল্য ইতিহাস', t: 'g' },
        { id: 'M16-rtv', en: 'RTV Lifecycle', bn: 'ফেরত জীবনচক্র', t: 'g' }] }
    ],
    reports: ['Spend by Category & Vendor', 'Match Exception Pareto', 'OTD by Vendor', 'Price Variance Alert',
              'Maverick Spend', 'PO Cycle Time'],
    // Data-entry forms = capture labels (sub-module order), then registry forms
    // with no backing model yet (each listed under `gaps`).
    forms: ['Purchase Requisition', 'Purchase Order', 'Vendor Invoice (3-way match)', 'RTV Request', 'RFQ',
            'GRN'],
    cross: ['M43 planned orders', 'M42 supplier gate', 'M52 invoices', 'M44 imports', 'P05 vendor portal'],
    freg: { src: 88, sub: [
      ['1', 'Demand Intake', 8], ['2', 'Requisition & Approval', 10], ['3', 'Consolidation', 6],
      ['4', 'RFQ & Bidding', 12], ['5', 'PO Lifecycle', 11], ['6', 'Blanket Orders', 6],
      ['7', 'Expediting', 7], ['8', 'GRN & Inspection', 9], ['9', '3-Way Match', 10],
      ['10', 'Spend Analysis', 9]] },
    // Capture map (CD-M16, A06 audit): cd_requisition, cd_ap_ext (M52 matcher), cd_consignment.
    // Every sub-module (freg) and screen opens the real Odoo form it captures into.
    captures: [
      { en: 'Purchase Requisition', bn: 'ক্রয় অনুরোধ', model: 'fix.requisition', freg: ['1', '2'], screens: ['M16-prs'] },
      { en: 'Purchase Order', bn: 'ক্রয় আদেশ', model: 'fix.purchase.order', freg: ['5'], screens: ['M16-pos'] },
      { en: 'Vendor Invoice (3-way match)', bn: 'সরবরাহকারী চালান (ত্রিমুখী মিলকরণ)', model: 'fix.vendor.invoice', freg: ['9'], screens: ['M16-match'] },
      { en: 'RTV Request', bn: 'ফেরত অনুরোধ', model: 'fix.consignment', ctx: { default_consignment_type: 'return_to_vendor' }, freg: [], screens: ['M16-rtv'] }
    ],
    // Gaps: no backing model in addons/ yet. Their buttons say so instead of
    // opening an unrelated form.
    gaps: [
      { en: 'Consolidation Run', freg: ['3'], screens: ['M16-consol'], note: 'no cross-branch consolidation model' },
      { en: 'RFQ', freg: ['4'], screens: ['M16-rfqs', 'M16-compare', 'M16-award'], note: 'no RFQ, bid or award model' },
      { en: 'Blanket Order', freg: ['6'], screens: ['M16-blanket'], note: 'no blanket / call-off agreement model' },
      { en: 'Expedite Action', freg: ['7'], screens: ['M16-expedite'], note: 'no expediting record' },
      { en: 'GRN', freg: ['8'], screens: ['M16-grn', 'M16-inspection'], note: 'no GRN or inspection model; receipt is only qty_received on fix.purchase.order.line' },
      { en: 'Spend Review', freg: ['10'], screens: ['M16-spend', 'M16-pricehist'], note: 'analysis only; no price history or spend model' }
    ]
  },

  M42: {
    area: 'A06', code: 'M42', en: 'Supplier Relationship', title: 'M42 · Supplier Relationship',
    bn: 'সরবরাহকারী সম্পর্ক', icon: '🧑‍💼',
    desc: 'Supplier qualification gate, scorecards, corrective actions, risk assessment, compliance screening.',
    kpis: [{ l: 'Qualified Suppliers' }, { l: 'Scorecard Avg' }, { l: 'CARs Open' },
           { l: 'Docs Expiring (60d)' }, { l: 'Single-Source Items' }, { l: 'Restricted Suppliers' }],
    groups: [
      { en: 'Register', screens: [
        { id: 'M42-suppliers', en: 'Supplier Directory', bn: 'সরবরাহকারী তালিকা', t: 'g' },
        { id: 'M42-segments', en: 'Segmentation', bn: 'সেগমেন্টেশন', t: 'g' },
        { id: 'M42-docs', en: 'Document Register', bn: 'দলিল রেজিস্টার', t: 'g' }] },
      { en: 'Qualification', screens: [
        { id: 'M42-qualification', en: 'Qualification Workflow', bn: 'যোগ্যতা যাচাই', t: 'c' },
        { id: 'M42-gate', en: 'Activation Gate (M16)', bn: 'অ্যাক্টিভেশন গেট', t: 'g' },
        { id: 'M42-requal', en: 'Re-Qualification', bn: 'পুনঃযোগ্যতা', t: 'g' }] },
      { en: 'Performance', screens: [
        { id: 'M42-scorecards', en: 'Scorecards', bn: 'স্কোরকার্ড', t: 'g' },
        { id: 'M42-cars', en: 'Corrective Actions', bn: 'সংশোধনী কর্ম', t: 'g' },
        { id: 'M42-reviews', en: 'Review Cycles', bn: 'পর্যালোচনা', t: 'c' }] },
      { en: 'Risk & Compliance', screens: [
        { id: 'M42-risk', en: 'Risk Assessment', bn: 'ঝুঁকি মূল্যায়ন', t: 'r' },
        { id: 'M42-screening', en: 'Sanctions / COI / ABAC', bn: 'স্ক্রিনিং', t: 'g' }] }
    ],
    reports: ['Supplier Scorecard League', 'CAR Closure Performance', 'Risk Heat Map', 'Contract Coverage',
              'Compliance Screening Log'],
    // Data-entry forms = capture labels (sub-module order), then registry forms
    // with no backing model yet (each listed under `gaps`).
    forms: ['Supplier Profile', 'Supplier Scorecard', 'CAR', 'Qualification Questionnaire', 'Risk Assessment'],
    cross: ['M33 party extension', 'M16 activation gate', 'P05 vendor portal', 'M40 brand class'],
    freg: { src: 71, sub: [
      ['1', 'Supplier Profiles', 9], ['2', 'Segmentation', 6], ['3', 'Qualification', 10],
      ['4', 'Documents & Validity', 8], ['5', 'Contracts & Price Lists', 7], ['6', 'Scorecards', 9],
      ['7', 'Corrective Actions', 7], ['8', 'Risk Assessment', 9], ['9', 'Compliance Screening', 6]] },
    // Capture map (CD-M42, A06 audit): cd_party_master (M33 party extension), cd_cx_feedback, cd_qms_process.
    // Every sub-module (freg) and screen opens the real Odoo form it captures into.
    captures: [
      { en: 'Supplier Profile', bn: 'সরবরাহকারী প্রোফাইল', model: 'fix.party.role', ctx: { default_role_type: 'vendor' }, freg: ['1'], screens: ['M42-suppliers'] },
      { en: 'Supplier Scorecard', bn: 'সরবরাহকারী স্কোরকার্ড', model: 'fix.supplier.scorecard', freg: ['6'], screens: ['M42-scorecards'] },
      { en: 'CAR', bn: 'সংশোধনী কর্ম অনুরোধ', model: 'fix.ncr', ctx: { default_source: 'supplier' }, freg: ['7'], screens: ['M42-cars'] }
    ],
    // Gaps: no backing model in addons/ yet. Their buttons say so instead of
    // opening an unrelated form.
    gaps: [
      { en: 'Supplier Segment', freg: ['2'], screens: ['M42-segments'], note: 'no supplier segmentation model' },
      { en: 'Qualification Questionnaire', freg: ['3'], screens: ['M42-qualification', 'M42-gate', 'M42-requal'], note: 'no qualification, activation gate or re-qualification model' },
      { en: 'Supplier Document', freg: ['4'], screens: ['M42-docs'], note: 'no supplier document validity model (fix.document has retention, not validity)' },
      { en: 'Supplier Contract & Price List', freg: ['5'], screens: [], note: 'no supplier contract or price list model' },
      { en: 'Review Cycle', freg: [], screens: ['M42-reviews'], note: 'no supplier review cycle model' },
      { en: 'Risk Assessment', freg: ['8'], screens: ['M42-risk'], note: 'no supplier risk model (fix.risk.register is the enterprise register, no supplier link)' },
      { en: 'Compliance Screening', freg: ['9'], screens: ['M42-screening'], note: 'no sanctions / COI / ABAC screening model' }
    ]
  },

  M43: {
    area: 'A06', code: 'M43', en: 'Demand Planning', title: 'M43 · Demand Planning',
    bn: 'চাহিদা পরিকল্পনা', icon: '📈',
    desc: 'Forecast orchestration with MAPE tracking, safety stock, reorder policies, multi-echelon rebalancing.',
    kpis: [{ l: 'Forecast MAPE' }, { l: 'Service Level Target' }, { l: 'Planned Orders' },
           { l: 'Stockout Incidents' }, { l: 'Excess Stock Value' }, { l: 'Rebalance Proposals' }],
    groups: [
      { en: 'Forecasting', screens: [
        { id: 'M43-history', en: 'History Assembly', bn: 'ইতিহাস সংকলন', t: 'g' },
        { id: 'M43-models', en: 'Model Orchestration', bn: 'মডেল অর্কেস্ট্রেশন', t: 'c' },
        { id: 'M43-accuracy', en: 'Accuracy & Bias (MAPE)', bn: 'নির্ভুলতা', t: 'r' }] },
      { en: 'Policies', screens: [
        { id: 'M43-segments', en: 'Part Segmentation', bn: 'পার্টস সেগমেন্টেশন', t: 'g' },
        { id: 'M43-safety', en: 'Safety Stock & ROP', bn: 'সেফটি স্টক', t: 'g' },
        { id: 'M43-leadtime', en: 'Lead-Time Modelling', bn: 'লিড-টাইম', t: 'g' }] },
      { en: 'Execution', screens: [
        { id: 'M43-planned', en: 'Planned Orders → PR', bn: 'পরিকল্পিত অর্ডার', t: 'g' },
        { id: 'M43-rebalance', en: 'Network Rebalancing', bn: 'নেটওয়ার্ক পুনঃসমন্বয়', t: 'c' },
        { id: 'M43-vanpar', en: 'Van-Stock Par Calculation', bn: 'ভ্যান প্যারামিটার', t: 'g' }] },
      { en: 'Simulation', screens: [
        { id: 'M43-whatif', en: 'What-If Simulation', bn: 'সিমুলেশন', t: 'c' }] }
    ],
    reports: ['Forecast Accuracy by Class', 'Stockout Root Causes', 'Excess & Obsolescence Exposure', 'Rebalancing Savings', 'New-Part Introduction'],
    // Data-entry forms = the capture labels below, in sub-module order
    // (registry forms 'Review Cycle', 'Policy Assignment', 'Rebalance Proposal' kept verbatim).
    forms: ['Demand History Adjustment', 'Part Segment Classification', 'Review Cycle', 'Forecast Override',
            'Demand Driver', 'Accuracy Review Note', 'Policy Assignment', 'Service-Level Target',
            'Lead-Time Profile', 'Planned Order', 'Rebalance Proposal', 'Network Stocking Policy',
            'Van Par Recommendation', 'What-If Simulation'],
    cross: ['M26 Forecast Models', 'M16 Planned Orders', 'M15 Stock Positions', 'M37 Lifecycle States'],
    freg: { src: 58, sub: [
      ['1', 'History & Cleansing', 7], ['2', 'Segmentation', 6], ['3', 'Forecast Orchestration', 8],
      ['4', 'Accuracy Tracking', 6], ['5', 'Safety Stock & ROP', 9], ['6', 'Lead-Time', 5],
      ['7', 'Planned Orders', 6], ['8', 'Multi-Echelon Rebalancing', 7], ['9', 'What-If', 4]] },
    // Capture map (cd_demand_plan, CD-M43-01): every sub-module (freg) and
    // every screen opens the real Odoo form it captures into.
    captures: [
      { en: 'Demand History Adjustment', bn: 'চাহিদা ইতিহাস সমন্বয়', model: 'fix.demand.adjustment', freg: ['1'], screens: ['M43-history'] },
      { en: 'Part Segment Classification', bn: 'পার্টস সেগমেন্ট শ্রেণীকরণ', model: 'fix.part.segment', freg: ['2'], screens: ['M43-segments'] },
      { en: 'Review Cycle', bn: 'পর্যালোচনা চক্র', model: 'fix.planning.run', freg: ['3'], screens: ['M43-models'] },
      { en: 'Forecast Override', bn: 'পূর্বাভাস পরিবর্তন', model: 'fix.forecast.override', freg: ['3'], screens: ['M43-models'] },
      { en: 'Demand Driver', bn: 'চাহিদা চালক', model: 'fix.demand.driver', freg: ['3'], screens: ['M43-models'] },
      { en: 'Accuracy Review Note', bn: 'নির্ভুলতা পর্যালোচনা নোট', model: 'fix.forecast.accuracy.review', freg: ['4'], screens: ['M43-accuracy'] },
      { en: 'Policy Assignment', bn: 'নীতি নির্ধারণ', model: 'fix.replenishment.parameter', freg: ['5'], screens: ['M43-safety'] },
      { en: 'Service-Level Target', bn: 'সার্ভিস লেভেল লক্ষ্য', model: 'fix.service.level.target', freg: ['5'], screens: ['M43-safety'] },
      { en: 'Lead-Time Profile', bn: 'লিড-টাইম প্রোফাইল', model: 'fix.lead.time.model', freg: ['6'], screens: ['M43-leadtime'] },
      { en: 'Planned Order', bn: 'পরিকল্পিত অর্ডার', model: 'fix.planned.order', freg: ['7'], screens: ['M43-planned'] },
      { en: 'Rebalance Proposal', bn: 'পুনঃসমন্বয় প্রস্তাব', model: 'fix.rebalance.proposal', freg: ['8'], screens: ['M43-rebalance'] },
      { en: 'Network Stocking Policy', bn: 'নেটওয়ার্ক স্টকিং নীতি', model: 'fix.network.policy', freg: ['8'], screens: ['M43-rebalance'] },
      { en: 'Van Par Recommendation', bn: 'ভ্যান প্যার সুপারিশ', model: 'fix.van.par.recommendation', freg: ['8'], screens: ['M43-vanpar'] },
      { en: 'What-If Simulation', bn: 'কী-যদি সিমুলেশন', model: 'fix.planning.simulation', freg: ['9'], screens: ['M43-whatif'] }
    ]
  },

  M44: {
    area: 'A06', code: 'M44', en: 'Import & Trade Compliance', title: 'M44 · Import & Trade Compliance',
    bn: 'আমদানি ও বাণিজ্য', icon: '🚢',
    desc: 'LC/TT lifecycle, HS classification, ASYCUDA Bill of Entry, duty cascade, landed-cost allocation.',
    kpis: [{ l: 'Active Imports' }, { l: 'LCs Open' }, { l: 'Duty Accuracy' }, { l: 'Demurrage Incidents' },
           { l: 'Landed-Cost Variance' }, { l: 'Cycle Time (order→release)' }],
    groups: [
      { en: 'Orders & Finance', screens: [
        { id: 'M44-orders', en: 'Import Orders', bn: 'আমদানি অর্ডার', t: 'g' },
        { id: 'M44-proforma', en: 'Proforma Invoices', bn: 'প্রোফর্মা', t: 'g' },
        { id: 'M44-lc', en: 'Letters of Credit', bn: 'এলসি', t: 'g' },
        { id: 'M44-incoterms', en: 'Incoterms & FX', bn: 'ইনকোটার্ম', t: 'g' }] },
      { en: 'Compliance', screens: [
        { id: 'M44-hs', en: 'HS Classification', bn: 'এইচএস কোড', t: 'g' },
        { id: 'M44-irc', en: 'IRC & Restrictions', bn: 'আইআরসি', t: 'g' },
        { id: 'M44-lca', en: 'LCA via Dealer Bank', bn: 'এলসিএ', t: 'g' }] },
      { en: 'Shipping & Customs', screens: [
        { id: 'M44-docs', en: 'Shipping Documents', bn: 'শিপিং দলিল', t: 'g' },
        { id: 'M44-arrival', en: 'Arrival & Port Handling', bn: 'বন্দর পরিচালনা', t: 'g' },
        { id: 'M44-boe', en: 'Bill of Entry (ASYCUDA)', bn: 'বিল অব এন্ট্রি', t: 'f' },
        { id: 'M44-duty', en: 'Duty Cascade (CD/RD/SD/VAT/AT/AIT)', bn: 'শুল্ক', t: 'r' }] },
      { en: 'Costing', screens: [
        { id: 'M44-landed', en: 'Landed Cost Allocation', bn: 'ল্যান্ডেড কস্ট', t: 'c' },
        { id: 'M44-cf', en: 'C&F Management', bn: 'সিঅ্যান্ডএফ', t: 'g' }] }
    ],
    reports: ['Landed Cost by Shipment', 'Duty & Tax Cascade', 'Cycle-Time Analysis', 'Demurrage Avoidance',
              'FX Exposure'],
    // Data-entry forms = capture labels (sub-module order), then registry forms
    // with no backing model yet (each listed under `gaps`).
    forms: ['Import Order', 'LC Application', 'HS Ruling Request', 'Bill of Entry'],
    cross: ['M16 import POs', 'M50 trade finance', 'M51 import VAT/duty', 'M15 landed cost'],
    freg: { src: 64, sub: [
      ['1', 'Import Order Lifecycle', 9], ['2', 'LC & Payments', 10], ['3', 'HS Classification', 7],
      ['4', 'Eligibility & IRC', 5], ['5', 'Shipping & Insurance', 8], ['6', 'Port & Customs', 9],
      ['7', 'Duty Computation', 8], ['8', 'Landed Cost', 8]] },
    // Capture map (CD-M44, A06 audit): cd_import_order. Only the order and its landed cost have a backend.
    // Every sub-module (freg) and screen opens the real Odoo form it captures into.
    captures: [
      { en: 'Import Order', bn: 'আমদানি অর্ডার', model: 'fix.import.order', freg: ['1', '8'], screens: ['M44-orders', 'M44-landed'] }
    ],
    // Gaps: no backing model in addons/ yet. Their buttons say so instead of
    // opening an unrelated form.
    gaps: [
      { en: 'Proforma Invoice', freg: [], screens: ['M44-proforma'], note: 'no proforma invoice model' },
      { en: 'LC Application', freg: ['2'], screens: ['M44-lc'], note: 'no letter of credit / TT payment model' },
      { en: 'Incoterm & FX Terms', freg: [], screens: ['M44-incoterms'], note: 'no incoterm or FX booking fields/model' },
      { en: 'HS Ruling Request', freg: ['3'], screens: ['M44-hs'], note: 'no HS classification model' },
      { en: 'IRC / LCA Record', freg: ['4'], screens: ['M44-irc', 'M44-lca'], note: 'no IRC or LCA eligibility model' },
      { en: 'Shipping Document', freg: ['5'], screens: ['M44-docs'], note: 'no shipping document or insurance model' },
      { en: 'Bill of Entry', freg: ['6'], screens: ['M44-arrival', 'M44-boe'], note: 'no port or Bill of Entry model' },
      { en: 'Duty Computation', freg: ['7'], screens: ['M44-duty'], note: 'no duty line model; customs duty is one amount on fix.import.order' },
      { en: 'C&F Agent Job', freg: [], screens: ['M44-cf'], note: 'no C&F agent model' }
    ]
  },

  /* ============ A07 · ASSETS & FACILITIES ============================== */
  M17: {
    area: 'A07', code: 'M17', en: 'Device & Asset Registry', title: 'M17 · Device & Asset Registry',
    bn: 'ডিভাইস রেজিস্ট্রি', icon: '📱',
    desc: 'Permanent identity per device — multi-identifier model, custody chain, service history, parts genealogy, estates.',
    kpis: [{ l: 'Registered Equipment' }, { l: 'Corporate Estates' }],
    groups: [
      { en: 'Registry', screens: [{ id: 'M17-assets', en: 'Master Equipment Directory', bn: 'ইকুইপমেন্ট ডিরেক্টরি', t: 'g' }] }
    ],
    reports: ['Installed Base by Brand'], forms: ['Register Customer Device'], cross: ['M01 Service Orders'],
    freg: { src: 96, sub: [['1', 'Multi-Identifier Model', 14], ['2', 'Repair Genealogy & History', 10]] }
  },

  M45: {
    area: 'A07', code: 'M45', en: 'Enterprise Assets & Test Equipment', title: 'M45 · Enterprise Assets & Test Equipment',
    bn: 'এন্টারপ্রাইজ সম্পদ', icon: '🔬',
    desc: 'Test instruments & tools — calibration management, tool crib issue/return, fitness states, usage per job.',
    kpis: [{ l: 'Calibrated Tools' }],
    groups: [
      { en: 'Tool Crib', screens: [{ id: 'M45-tools', en: 'Workshop Equipment & Tools Register', bn: 'টুলস ও ইকুইপমেন্ট রেজিস্টার', t: 'g' }] }
    ],
    reports: ['Calibration Expiry Forecast'], forms: ['Log Calibration Certificate'], cross: ['M23 ISO 9001'],
    freg: { src: 76, sub: [['1', 'Calibration Schedule & Certification', 10], ['2', 'Tool Check-out & Return', 8]] }
  },

  M46: {
    area: 'A07', code: 'M46', en: 'Fleet & Vehicles', title: 'M46 · Fleet & Vehicles',
    bn: 'ফ্লিট ও যানবাহন', icon: '🚚',
    desc: 'Vans & bikes — statutory documents with expiry control, fuel efficiency, telematics, cost per km.',
    kpis: [{ l: 'Active Leases' }],
    groups: [
      { en: 'Leases', screens: [{ id: 'M46-leases', en: 'Branch Lease Agreements', bn: 'শাখা লিজ চুক্তি', t: 'g' }] }
    ],
    reports: ['Rent & Utility Schedules'], forms: ['Record Lease Renewal'], cross: ['M19 Finance'],
    freg: { src: 70, sub: [['1', 'Lease Term & Payment Tracking', 8], ['2', 'Facility Safety Audits', 6]] }
  },

  M47: {
    area: 'A07', code: 'M47', en: 'Facility & Branch Infrastructure', title: 'M47 · Facility & Branch Infrastructure',
    bn: 'সুবিধা ও শাখা', icon: '🏬',
    desc: '51+ sites — lease administration, statutory licences, utilities, branch infrastructure, safety equipment.',
    kpis: [{ l: 'Active Fleet Vehicles' }],
    groups: [
      { en: 'Fleet', screens: [{ id: 'M47-vehicles', en: 'Fleet Vehicles Register', bn: 'ফ্লিট যানবাহন তালিকা', t: 'g' }] }
    ],
    reports: ['Vehicle Fuel & Mileage Log'], forms: ['Log Vehicle Maintenance'], cross: ['M02 Field Dispatch'],
    freg: { src: 74, sub: [['1', 'Vehicle Maintenance Scheduling', 8], ['2', 'Fuel Card Reconciliation', 8]] }
  },

  M48: {
    area: 'A07', code: 'M48', en: 'IoT Telemetry & Predictive', title: 'M48 · IoT Telemetry & Predictive',
    bn: 'আইওটি ও পূর্বাভাস', icon: '📡',
    desc: 'TimescaleDB hypertables, threshold alerting, asset health scoring, failure prediction, prescriptive routing.',
    kpis: [{ l: 'Internal IT Assets' }],
    groups: [
      { en: 'IT Assets', screens: [{ id: 'M48-it', en: 'Internal IT Asset Inventory', bn: 'আইটি সম্পদ ইনভেন্টরি', t: 'g' }] }
    ],
    reports: ['Software License Compliance'], forms: ['Assign IT Asset to Employee'], cross: ['M21 Workforce'],
    freg: { src: 68, sub: [['1', 'Hardware & License Asset Master', 8], ['2', 'Security Patch Audit', 6]] }
  },

  /* ============ A08 · FINANCE & TREASURY =============================== */
  M19: {
    area: 'A08', code: 'M19', en: 'Financial Accounting & GL', title: 'M19 · Financial Accounting & GL',
    bn: 'আর্থিক হিসাব', icon: '💰',
    desc: 'Chart of accounts, 7-dimension model, subledger posting engine, July–June close, statutory statements.',
    kpis: [
      { l: 'Revenue MTD' },
      { l: 'Operating Margin' }
    ],
    groups: [
      {
        en: 'General Ledger',
        screens: [
          { id: 'M19-journals', en: 'Journal Entries (Auto-Posted)', bn: 'জার্নাল এন্ট্রি', t: 'g' },
          { id: 'M19-tb', en: 'Trial Balance & Financials', bn: 'ট্রায়াল ব্যালেন্স', t: 'r' }
        ]
      }
    ],
    reports: ['Monthly Profit & Loss Statement', 'Balance Sheet Statement', 'Branch Profitability Report'],
    forms: ['Create Manual Journal Entry'], cross: ['M20 Invoicing', 'M50 Accounts Payable'],
    freg: { src: 118, sub: [['1', 'Automated Subledger Posting', 14], ['2', 'Financial Statement Generation', 12]] }
  },

  M20: {
    area: 'A08', code: 'M20', en: 'AR, Invoicing & Collections', title: 'M20 · AR, Invoicing & Collections',
    bn: 'প্রাপ্য ও ইনভয়েসিং', icon: '🧾',
    desc: 'Billable events from every module, Mushak 6.3 invoices, bKash/Nagad/card receipts, dunning, ageing.',
    kpis: [
      { l: 'Mushak 6.3 Invoices MTD' },
      { l: 'VAT Collected (15%)' },
      { l: 'NBR Compliant' }
    ],
    groups: [
      {
        en: 'Tax Invoices',
        screens: [
          { id: 'M20-invoices', en: 'All Mushak 6.3 Tax Invoices', bn: 'সকল মূসক ৬.৩ চালান', t: 'g' },
          { id: 'M20-preview', en: 'Mushak 6.3 Invoice Printable', bn: 'চালান প্রিন্ট ভিউ', t: 'f' }
        ]
      }
    ],
    reports: ['Monthly NBR Mushak 9.1 VAT Return', 'Withholding Tax (VDS) Summary'],
    forms: ['Generate Mushak 6.3 Invoice Form', 'Credit Note (Mushak 6.7) Form'],
    cross: ['M01 Service Orders', 'M19 General Ledger', 'M54 Tax Filing'],
    freg: { src: 110, sub: [['1', 'NBR Mushak 6.3 Calculation Engine', 14], ['2', 'QR Code Digital Validation', 10], ['3', 'Mushak 9.1 Return Compilation', 12]] }
  },

  M52: {
    area: 'A08', code: 'M52', en: 'AP & Employee Expense', title: 'M52 · AP & Employee Expense',
    bn: 'প্রদেয় ও ব্যয়', icon: '💸',
    desc: 'Vendor invoices with 3-way match, TDS/VDS at source, employee expenses & advances, payment runs.',
    kpis: [{ l: 'Total AR Outstanding' }, { l: 'Overdue > 60d' }],
    groups: [
      { en: 'Receivables', screens: [{ id: 'M52-ar', en: 'AR Ageing Analysis Register', bn: 'রিসিভেবল এজিং', t: 'g' }] }
    ],
    reports: ['AR Aging 30/60/90 Days Pareto'], forms: ['Record Customer Payment Receipt'], cross: ['M36 B2B Accounts', 'M19 Ledger'],
    freg: { src: 86, sub: [['1', 'Aging Calculation & Provisioning', 10], ['2', 'Automated Dunning Reminders', 8]] }
  },

  M50: {
    area: 'A08', code: 'M50', en: 'Treasury & Banking', title: 'M50 · Treasury & Banking',
    bn: 'কোষাগার ও ব্যাংক', icon: '🏦',
    desc: 'Bank reconciliation, branch cash consolidation, rider COD, gateway/MFS settlement, BEFTN/RTGS execution.',
    kpis: [{ l: 'Pending Vendor Bills' }],
    groups: [
      { en: 'Payables', screens: [{ id: 'M50-bills', en: 'Vendor Bills & Invoices', bn: 'ভেন্ডর বিল তালিকা', t: 'g' }] }
    ],
    reports: ['Upcoming Payment Commitments'], forms: ['Record Vendor Bill'], cross: ['M41 Purchase Orders', 'M19 Ledger'],
    freg: { src: 88, sub: [['1', '3-Way Match Verification', 10], ['2', 'TDS / VDS Statutory Deduction', 8]] }
  },

  M51: {
    area: 'A08', code: 'M51', en: 'Tax & Regulatory (BD)', title: 'M51 · Tax & Regulatory (BD)',
    bn: 'কর ও ভ্যাট', icon: '🏛️',
    desc: 'VAT 15%, Mushak 6.1–9.1 registers & returns, TDS/VDS, challans, NID capture, statutory calendar.',
    kpis: [{ l: 'Reconciliation Health' }],
    groups: [
      { en: 'Reconciliation', screens: [{ id: 'M51-reconcile', en: 'Bank & Mobile Wallet Statement Match', bn: 'ব্যাংক স্টেটমেন্ট ম্যাচ', t: 'g' }] }
    ],
    reports: ['Unreconciled Bank Transactions'], forms: ['Perform Bank Reconciliation'], cross: ['M19 General Ledger'],
    freg: { src: 80, sub: [['1', 'Bank Feed Parsing & Auto-Match', 10], ['2', 'bKash / Nagad Settlement Cleared', 8]] }
  },

  M53: {
    area: 'A08', code: 'M53', en: 'Revenue Recognition & Settlement', title: 'M53 · Revenue Recognition & Settlement',
    bn: 'রাজস্ব ও নিষ্পত্তি', icon: '📊',
    desc: 'Performance obligations, contract balances, commission ledger, seller/partner payouts, clawbacks, escrow.',
    kpis: [{ l: 'Budget Variance MTD' }],
    groups: [
      { en: 'Budgets', screens: [{ id: 'M53-budgets', en: 'Cost Center Budget Master', bn: 'কস্ট সেন্টার বাজেট', t: 'g' }] }
    ],
    reports: ['Budget vs Actual Variance Report'], forms: ['Create Annual Branch Budget'], cross: ['M19 Ledger'],
    freg: { src: 76, sub: [['1', 'Cost Center Allocation Rules', 8], ['2', 'Variance Alerting Engine', 8]] }
  },

  M49: {
    area: 'A08', code: 'M49', en: 'Fixed Assets & Capex', title: 'M49 · Fixed Assets & Capex',
    bn: 'স্থায়ী সম্পদ ও ক্যাপেক্স', icon: '🏗️',
    desc: 'Capex requests to retirement — CWIP, dual-book depreciation (accounting + tax Third Schedule), verification.',
    kpis: [{ l: 'Net Book Value' }],
    groups: [
      { en: 'Fixed Assets', screens: [{ id: 'M49-assets', en: 'Fixed Assets Register', bn: 'স্থাবর সম্পদ রেজিস্টার', t: 'g' }] }
    ],
    reports: ['Annual Depreciation Schedule'], forms: ['Add Fixed Asset'], cross: ['M19 General Ledger'],
    freg: { src: 68, sub: [['1', 'Depreciation Run Generator', 8], ['2', 'Asset Disposal & Gain/Loss', 6]] }
  },

  M54: {
    area: 'A08', code: 'M54', en: 'Costing, Budget & FP&A', title: 'M54 · Costing, Budget & FP&A',
    bn: 'ব্যয়, বাজেট ও এফপিএ', icon: '🧮',
    desc: 'Allocation cycles, job & contract costing, 14-stream business-line profitability, branch league, budgets.',
    kpis: [{ l: 'Audit Readiness Score' }],
    groups: [
      { en: 'Audit', screens: [{ id: 'M54-audit', en: 'Statutory Audit Document Vault', bn: 'অডিট ডকুমেন্ট ভল্ট', t: 'g' }] }
    ],
    reports: ['Annual Tax Schedule Package'], forms: ['Generate Statutory Audit File'], cross: ['M20 Mushak 6.3'],
    freg: { src: 72, sub: [['1', 'Audit Trail Export & Reconciliation', 8], ['2', 'NBR Compliance Check', 8]] }
  },

  /* ============ A09 · PEOPLE & WORKFORCE =============================== */
  M21: {
    area: 'A09', code: 'M21', en: 'Core HR & Lifecycle', title: 'M21 · Core HR & Lifecycle',
    bn: 'মানবসম্পদ', icon: '👥',
    desc: 'Hire-to-retire, Labour Act documents (appointment letter, ID card, service book), org structure, ESS/MSS.',
    kpis: [{ l: 'Active Technicians' }, { l: 'Avg Skill Rating' }],
    groups: [
      { en: 'Workforce', screens: [{ id: 'M21-roster', en: 'Technician Skills & Certification Directory', bn: 'টেকনিশিয়ান দক্ষতা ডিরেক্টরি', t: 'g' }] }
    ],
    reports: ['Skill Gap Analysis by Branch'], forms: ['Add Technician Skill Certification'], cross: ['M02 Dispatch', 'M56 Payroll'],
    freg: { src: 94, sub: [['1', 'Multi-Tier Skill Matrix (L1-L4)', 12], ['2', 'Brand Certification Compliance', 10]] }
  },

  M55: {
    area: 'A09', code: 'M55', en: 'Time, Attendance & Scheduling', title: 'M55 · Time, Attendance & Scheduling',
    bn: 'সময় ও শিফট', icon: '⏰',
    desc: 'Biometric + geofenced mobile capture, moon-dependent holidays, rosters, availability published to dispatch.',
    kpis: [{ l: 'Present Today' }],
    groups: [
      { en: 'Attendance', screens: [{ id: 'M55-clock', en: 'Biometric Attendance Live Feed', bn: 'বায়োমেট্রিক উপস্থিতি লাইভ', t: 'g' }] }
    ],
    reports: ['Monthly Attendance & Overtime'], forms: ['Regularize Missed Punch'], cross: ['M56 Payroll'],
    freg: { src: 82, sub: [['1', 'Biometric Hardware Polling', 10], ['2', 'Field GPS Check-In Geo-fence', 8]] }
  },

  M56: {
    area: 'A09', code: 'M56', en: 'Payroll & Statutory', title: 'M56 · Payroll & Statutory',
    bn: 'বেতন ও সুবিধা', icon: '💵',
    desc: 'BD gross-to-net engine, tax slabs AY26-27, PF, gratuity ≥30 days/yr, festival bonus, BEFTN bank files.',
    kpis: [{ l: 'Monthly Payroll Run' }],
    groups: [
      { en: 'Payroll', screens: [{ id: 'M56-payroll', en: 'Monthly Salary Processing Register', bn: 'বেতন প্রসেসিং রেজিস্টার', t: 'g' }] }
    ],
    reports: ['Bank Salary Disbursement Advice'], forms: ['Run Monthly Payroll'], cross: ['M19 General Ledger', 'M21 Workforce'],
    freg: { src: 90, sub: [['1', 'Salary Calculation with Deductions', 12], ['2', 'Electronic Bank File Generator', 8]] }
  },

  M57: {
    area: 'A09', code: 'M57', en: 'Performance & Incentives', title: 'M57 · Performance & Incentives',
    bn: 'পারফরম্যান্স ও প্রণোদনা', icon: '🏆',
    desc: 'Goal cascades, KPI attribution to payroll, technician incentive schemes, calibration, recognition.',
    kpis: [{ l: 'Incentives Earned MTD' }],
    groups: [
      { en: 'Incentives', screens: [{ id: 'M57-leaderboard', en: 'Technician Incentive Leaderboard', bn: 'ইনসেন্টিভ লিডারবোর্ড', t: 'd' }] }
    ],
    reports: ['Technician Bonus Distribution'], forms: ['Approve Monthly Incentives'], cross: ['M56 Payroll', 'M01 Service Orders'],
    freg: { src: 84, sub: [['1', 'FTF & CSAT Bonus Calculation', 10], ['2', 'Monthly Leaderboard Publisher', 8]] }
  },

  M22: {
    area: 'A09', code: 'M22', en: 'Learning & Certification', title: 'M22 · Learning & Certification',
    bn: 'প্রশিক্ষণ ও সার্টিফিকেশন', icon: '🎓',
    desc: 'Competency framework, brand certification register with expiry, hard block on expired certification at dispatch.',
    kpis: [{ l: 'Mobile Apps Active' }],
    groups: [
      { en: 'Mobile Fleet', screens: [{ id: 'M22-fleet', en: 'Field Tech Mobile Connectivity Monitor', bn: 'মোবাইল কানেক্টিভিটি মনিটর', t: 'g' }] }
    ],
    reports: ['Offline Sync Discrepancy Log'], forms: ['Remote Device Reset Request'], cross: ['M02 Field Dispatch'],
    freg: { src: 76, sub: [['1', 'PWA Device Telemetry Heartbeat', 8], ['2', 'Local SQLite Cache Sync Audit', 8]] }
  },

  M58: {
    area: 'A09', code: 'M58', en: 'Talent Acquisition', title: 'M58 · Talent Acquisition',
    bn: 'নিয়োগ', icon: '🧲',
    desc: 'Requisitions vs budget, structured interviews, practical technician assessments, pre-boarding, PDPA erasure.',
    kpis: [{ l: 'Certified Techs' }],
    groups: [
      { en: 'Training', screens: [{ id: 'M58-courses', en: 'Academy Training Programs & Scores', bn: 'ট্রেনিং প্রোগ্রাম তালিকা', t: 'g' }] }
    ],
    reports: ['Certification Expiry Alert'], forms: ['Register for Brand Exam'], cross: ['M21 Skills'],
    freg: { src: 70, sub: [['1', 'Training Module Curriculum Log', 8], ['2', 'Exam Score Verification', 6]] }
  },

  M59: {
    area: 'A09', code: 'M59', en: 'Health, Safety & Wellbeing', title: 'M59 · Health, Safety & Wellbeing',
    bn: 'স্বাস্থ্য ও নিরাপত্তা', icon: '🦺',
    desc: 'Hazard register, lone-worker safety, battery/electrical hazards, statutory accident clock, safety committee.',
    kpis: [{ l: 'Incident-Free Days' }],
    groups: [
      { en: 'Safety', screens: [{ id: 'M59-incidents', en: 'Safety Incident & Hazard Log', bn: 'নিরাপত্তা ঘটনা ও হ্যাজার্ড লগ', t: 'g' }] }
    ],
    reports: ['Annual EHS Safety Audit'], forms: ['Log Safety Incident Form'], cross: ['M23 ISO 9001'],
    freg: { src: 68, sub: [['1', 'Hazard Reporting & Root Cause', 8], ['2', 'PPE & Cleanroom ESD Audit', 6]] }
  },

  /* ============ A10 · QUALITY & GOVERNANCE ============================= */
  M23: {
    area: 'A10', code: 'M23', en: 'Quality Management (ISO)', title: 'M23 · Quality Management (ISO)',
    bn: 'কোয়ালিটি ম্যানেজমেন্ট', icon: '✅',
    desc: 'ISO 9001:2015 operating system — process register, NCRs, CAPA with verification, audits, management review.',
    kpis: [{ l: 'QMS Audit Score' }, { l: 'Open NCRs' }],
    groups: [
      { en: 'ISO Compliance', screens: [{ id: 'M23-audits', en: 'ISO 9001:2015 Quality Audit Logs', bn: 'আইএসও অডিট লগ', t: 'g' }] }
    ],
    reports: ['Annual ISO Surveillance Audit Report'], forms: ['Log Non-Conformance (NCR) Form'], cross: ['M60 Rework Analysis'],
    freg: { src: 98, sub: [['1', 'QMS Internal Audit Schedule', 12], ['2', 'Non-Conformance & CAPA Engine', 10]] }
  },

  M60: {
    area: 'A10', code: 'M60', en: 'Governance, Risk & Compliance', title: 'M60 · Governance, Risk & Compliance',
    bn: 'গভর্নেন্স ও ঝুঁকি', icon: '⚖️',
    desc: 'Enterprise risk register, internal control testing, SoD rules, licence register, PDPA governance, whistleblowing.',
    kpis: [{ l: 'Rework Rate' }],
    groups: [
      { en: 'Rework Analysis', screens: [{ id: 'M60-rework', en: 'Repeat-Fault Rework Investigations', bn: 'পুনরাবৃত্ত ত্রুটি তদন্ত', t: 'g' }] }
    ],
    reports: ['Rework Pareto by Component'], forms: ['Initiate CAPA Investigation'], cross: ['M01 Service Orders', 'M23 ISO 9001'],
    freg: { src: 84, sub: [['1', 'Repeat Repair Trigger & Detection', 10], ['2', 'Root Cause CAPA Recommendation', 8]] }
  },

  M24: {
    area: 'A10', code: 'M24', en: 'Documents & E-Signature', title: 'M24 · Documents & E-Signature',
    bn: 'দলিল ও ই-স্বাক্ষর', icon: '🗂️',
    desc: 'Auto-filing from transactions, bilingual OCR search, e-signature envelopes, retention 5–10y, evidence packs.',
    kpis: [{ l: 'DoE Green Score' }],
    groups: [
      { en: 'EHS', screens: [{ id: 'M24-env', en: 'Environmental Compliance Audits', bn: 'পরিবেশ অডিট', t: 'g' }] }
    ],
    reports: ['Annual DoE Compliance Report'], forms: ['Hazardous Waste Disposal Manifest'], cross: ['M13 E-Waste'],
    freg: { src: 72, sub: [['1', 'Hazardous Waste Neutralization Log', 8], ['2', 'Government DoE Filing', 6]] }
  },

  M61: {
    area: 'A10', code: 'M61', en: 'Knowledge & Technical Library', title: 'M61 · Knowledge & Technical Library',
    bn: 'জ্ঞান ও কারিগরি লাইব্রেরি', icon: '📚',
    desc: 'Repair procedures & fault→fix, troubleshooting trees, offline distribution to technician app, brand bulletins.',
    kpis: [{ l: 'Active SOPs' }],
    groups: [
      { en: 'SOPs', screens: [{ id: 'M61-sops', en: 'Standard Operating Procedures Library', bn: 'এসওপি লাইব্রেরি', t: 'g' }] }
    ],
    reports: ['SOP Readership & Compliance'], forms: ['Publish New Repair SOP'], cross: ['M21 Skills'],
    freg: { src: 74, sub: [['1', 'SOP Version Control & Approval', 8], ['2', 'Disassembly Guide Publisher', 8]] }
  },

  /* ============ A11 · INSIGHTS & INTELLIGENCE ========================== */
  M25: {
    area: 'A11', code: 'M25', en: 'Business Intelligence', title: 'M25 · Business Intelligence',
    bn: 'বিজনেস ইন্টেলিজেন্স', icon: '📊',
    desc: 'Role dashboards, standard report library, embedded analytics, scheduled bursting, spreadsheet retirement.',
    kpis: [{ l: 'BI Data Freshness' }],
    groups: [
      { en: 'BI Dashboards', screens: [{ id: 'M25-bi', en: 'Executive C-Suite KPI Dashboard', bn: 'এক্সিকিউটিভ ড্যাশবোর্ড', t: 'd' }] }
    ],
    reports: ['Weekly Executive Business Review'], forms: ['Configure Power BI Sync'], cross: ['All Modules'],
    freg: { src: 88, sub: [['1', 'Data Warehouse ETL Extraction', 10], ['2', 'Executive Metric Aggregator', 10]] }
  },

  M26: {
    area: 'A11', code: 'M26', en: 'AI/ML Services (14 models)', title: 'M26 · AI/ML Services (14 models)',
    bn: 'এআই/এমএল সেবা', icon: '🧠',
    desc: 'Dispatch scoring 70% auto-assign, fault classification from Bengali text, demand MAPE<22%, trade-in valuation.',
    kpis: [{ l: 'AI Prediction Accuracy' }],
    groups: [
      { en: 'AI Models', screens: [{ id: 'M26-ai', en: 'Predictive Failure Predictions', bn: 'প্রেডিক্টিভ ফেইলিউর মডেল', t: 'd' }] }
    ],
    reports: ['Model Accuracy & Retraining Log'], forms: ['Run ML Model Inference'], cross: ['M02 Dispatch', 'M15 Parts'],
    freg: { src: 94, sub: [['1', 'Failure Probability Scoring', 12], ['2', 'Timefold Route Optimizer', 12]] }
  },

  M62: {
    area: 'A11', code: 'M62', en: 'Data Platform & Governance', title: 'M62 · Data Platform & Governance',
    bn: 'ডেটা প্ল্যাটফর্ম', icon: '🗃️',
    desc: 'Medallion lakehouse, dimensional model, semantic metric registry (one certified number), lineage, masking.',
    kpis: [{ l: 'Average Gross Margin' }],
    groups: [
      { en: 'Profitability', screens: [{ id: 'M62-margin', en: 'Job & Device Profitability Matrix', bn: 'মার্জিন ম্যাট্রিক্স', t: 'r' }] }
    ],
    reports: ['Brand-Wise Net Contribution'], forms: ['Run Margin Simulation'], cross: ['M19 Finance', 'M01 Orders'],
    freg: { src: 82, sub: [['1', 'Job-Level Unit Economics', 10], ['2', 'Overhead Cost Absorption Model', 8]] }
  },

  M63: {
    area: 'A11', code: 'M63', en: 'Process Automation', title: 'M63 · Process Automation',
    bn: 'প্রসেস অটোমেশন', icon: '⚙️',
    desc: 'Workflow engine with approval chains, DoA matrix, business-rule repository, unified task inbox, escalation.',
    kpis: [{ l: 'Events Processed/Sec' }],
    groups: [
      { en: 'Live Pulse', screens: [{ id: 'M63-pulse', en: 'Real-Time Event Stream Monitor', bn: 'লাইভ ইভেন্ট মনিটর', t: 'd' }] }
    ],
    reports: ['System Alert Frequency Log'], forms: ['Broadcast Emergency Notice'], cross: ['All Modules'],
    freg: { src: 80, sub: [['1', 'WebSocket Event Broadcasting', 10], ['2', 'Rule-Based Alert Trigger Engine', 8]] }
  },

  /* ============ A12 · PLATFORM & TECHNOLOGY ============================ */
  M28: {
    area: 'A12', code: 'M28', en: 'Integration, API & Events', title: 'M28 · Integration, API & Events',
    bn: 'ইন্টিগ্রেশন ও এপিআই', icon: '🔌',
    desc: 'API gateway, 47 external connectors (bKash/Nagad/SSLCOMMERZ/Google Maps/Traccar), event bus, offline sync.',
    kpis: [{ l: 'Gateway Uptime' }],
    groups: [
      { en: 'APIs', screens: [{ id: 'M28-gateway', en: 'API Traffic & Webhook Monitor', bn: 'এপিআই ট্রাফিক মনিটর', t: 'd' }] }
    ],
    reports: ['API Latency & Error Rate Log'], forms: ['Generate API Secret Key'], cross: ['All Systems'],
    freg: { src: 90, sub: [['1', 'Secure OAuth2 & HMAC Verification', 10], ['2', 'BullMQ Background Event Dispatch', 10]] }
  },

  M29: {
    area: 'A12', code: 'M29', en: 'Identity, Access & Security', title: 'M29 · Identity, Access & Security',
    bn: 'পরিচয় ও নিরাপত্তা', icon: '🔐',
    desc: 'MFA everywhere, 6 data-isolation tiers T0–T5, field-level permissions, SoD enforcement, immutable audit.',
    kpis: [{ l: 'Active ERP Users' }],
    groups: [
      { en: 'Security', screens: [{ id: 'M29-rbac', en: 'Role & Permission Assignment', bn: 'ভূমিকা ও পারমিশন', t: 'g' }] }
    ],
    reports: ['Security Access Audit Trail'], forms: ['Assign User Roles'], cross: ['System Core'],
    freg: { src: 88, sub: [['1', 'Field-Level Permission Matrix', 10], ['2', 'Tamper-Evident Action Audit Log', 8]] }
  },

  M30: {
    area: 'A12', code: 'M30', en: 'Platform Administration', title: 'M30 · Platform Administration',
    bn: 'প্ল্যাটফর্ম প্রশাসন', icon: '🛠️',
    desc: 'Legal entities, 51+ branch register with <1-day provisioning, config registry, feature flags, health console.',
    kpis: [{ l: 'Privacy Compliance' }],
    groups: [
      { en: 'Privacy', screens: [{ id: 'M30-privacy', en: 'Data Residency & Anonymization Log', bn: 'ডাটা রেসিডেন্সি লগ', t: 'g' }] }
    ],
    reports: ['PDPA Compliance Certification'], forms: ['Process Data Erasure Request'], cross: ['M07 Customers'],
    freg: { src: 76, sub: [['1', 'PII Field Encryption & Masking', 8], ['2', 'Customer Data Export / Deletion', 8]] }
  },

  M64: {
    area: 'A12', code: 'M64', en: 'Master Data Management', title: 'M64 · Master Data Management',
    bn: 'মাস্টার ডেটা', icon: '🧬',
    desc: 'Domain ownership, stewardship workflow as only change path, DQ rule engine, golden-record survivorship.',
    kpis: [{ l: 'Sync Queue Latency' }],
    groups: [
      { en: 'Sync Engine', screens: [{ id: 'M64-sync', en: 'Mobile Offline Queue & Conflict Monitor', bn: 'অফলাইন কিউ মনিটর', t: 'd' }] }
    ],
    reports: ['Sync Conflict Resolution Log'], forms: ['Force Full Offline Re-sync'], cross: ['M02 Field Service'],
    freg: { src: 78, sub: [['1', 'CRDT Delta Synchronization', 10], ['2', 'Conflict Auto-Resolution Engine', 8]] }
  },

  M65: {
    area: 'A12', code: 'M65', en: 'Multi-Entity & Localisation', title: 'M65 · Multi-Entity & Localisation',
    bn: 'বহু-সত্তা ও স্থানীয়করণ', icon: '🌍',
    desc: 'Country packs, bn-BD ICU collation & phonetic input, lakh/crore grouping, residency rules, expansion gateways.',
    kpis: [{ l: 'Scheduled Jobs' }],
    groups: [
      { en: 'Scheduler', screens: [{ id: 'M65-jobs', en: 'Cron & Airflow Scheduled Jobs', bn: 'শিডিউলড জব তালিকা', t: 'g' }] }
    ],
    reports: ['Nightly Batch Job Duration'], forms: ['Trigger Immediate Batch Job'], cross: ['System Core'],
    freg: { src: 70, sub: [['1', 'Distributed Cron Execution Engine', 8], ['2', 'Job Failure Auto-Retry & Alert', 6]] }
  },

  M66: {
    area: 'A12', code: 'M66', en: 'Internal IT Service', title: 'M66 · Internal IT Service',
    bn: 'অভ্যন্তরীণ আইটি সেবা', icon: '🖥',
    desc: 'Employee service catalogue, incidents & changes, IT asset lifecycle, licence optimisation, CMDB.',
    kpis: [{ l: 'Master Data Health' }],
    groups: [
      { en: 'Governance', screens: [{ id: 'M66-master', en: 'Master Data Golden Records & Rules', bn: 'মাস্টার ডাটা গোল্ডেন রেকর্ড', t: 'g' }] }
    ],
    reports: ['Duplicate Entity Report'], forms: ['Approve Entity Merge'], cross: ['All Masters'],
    freg: { src: 74, sub: [['1', 'Fuzzy Matching Deduplication', 8], ['2', 'Golden Record Hierarchy Enforcer', 8]] }
  },

  M67: {
    area: 'A12', code: 'M67', en: 'Projects & Portfolio', title: 'M67 · Projects & Portfolio',
    bn: 'প্রকল্প ও পোর্টফোলিও', icon: '📁',
    desc: 'Branch openings, rollouts, bulk decommissions — WBS, earned value, milestone billing, portfolio stage gates.',
    kpis: [
      { l: 'CPU Utilization' },
      { l: 'DB Connection Pool' },
      { l: 'Redis Hit Ratio' }
    ],
    groups: [
      { en: 'Telemetry', screens: [{ id: 'M67-telemetry', en: 'Live Server Telemetry & System Health', bn: 'সার্ভার টেলিমেট্রি ড্যাশবোর্ড', t: 'd' }] }
    ],
    reports: ['System Resource Utilization Log'], forms: ['Flush Application Cache'], cross: ['Infrastructure'],
    freg: { src: 82, sub: [['1', 'OpenTelemetry Metrics Harvester', 10], ['2', 'Database Slow Query Watcher', 8]] }
  }
};

/* =====================================================================
 * Screen column schemas (data-shape parity, FF-45).
 * Columns come from the prototype's grid contract; ROWS ARE NEVER
 * FABRICATED — the workspace fills them from live backend reads where a
 * surface exists (e.g. fix.service.order) and renders an empty state
 * otherwise (03-DATA-STRATEGY: no demo rows).
 * ===================================================================== */
export function generateGridData(screenId, groupTitle, moduleTitle) {
  const query = `${screenId} ${groupTitle} ${moduleTitle}`.toLowerCase();

  if (/order|intake|hotline|queue|request|token|wip|rework/.test(query)) {
    return { cols: ['Order No', 'Customer', 'Device / Model', 'Branch', 'Technician', 'Status', 'SLA Target', 'Total Amount', '15% VAT'], rows: [] };
  }
  if (/work|dispatch|wo|field|tech|route|zone/.test(query)) {
    return { cols: ['WO Number', 'Assigned Tech', 'Territory Zone', 'Customer', 'Scheduled Time', 'Status', 'ETA', 'Action'], rows: [] };
  }
  if (/inventory|stock|part|bin|reorder|warehouse/.test(query)) {
    return { cols: ['Part SKU', 'Description', 'Brand', 'On-Hand', 'Reserved', 'Available', 'Bin Location', 'Unit Price', 'Total Value'], rows: [] };
  }
  if (/invoice|mushak|bill|vat|journal|ar|ledger/.test(query)) {
    return { cols: ['Mushak 6.3 No', 'Customer Name', 'Issue Date', 'Taxable Value', '15% VAT (BDT)', 'Grand Total (BDT)', 'Payment Method', 'NBR Status'], rows: [] };
  }
  return { cols: ['Record ID', 'Title / Description', 'Category', 'Assigned Hub', 'Created Date', 'Status', 'Actions'], rows: [] };
}
