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
    cross: ['M01 Service Orders', 'M43 Transit Tracking', 'M47 Logistics Fleet'],
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
    kpis: [
      { l: 'Total Inventory Value' },
      { l: 'Parts Stock-Out Rate' },
      { l: 'Inventory Accuracy' }
    ],
    groups: [
      {
        en: 'Parts Management',
        screens: [
          { id: 'M15-stock', en: 'Parts Stock by Branch (53 Hubs)', bn: 'সকল শাখার স্টক', t: 'g' },
          { id: 'M15-reserved', en: 'Reserved Parts for Active Jobs', bn: 'রিজার্ভড পার্টস', t: 'g' },
          { id: 'M15-reorder', en: 'Min/Max Auto-Reorder Alerts', bn: 'অটো রি-অর্ডার অ্যালার্ট', t: 'g' }
        ]
      }
    ],
    reports: ['Inventory Valuation by Class', 'Fast vs Slow Moving Parts Pareto', 'Branch Stock Discrepancy Log'],
    forms: ['Stock Adjustment Request', 'Issue Parts to Service Order', 'Bin Transfer Voucher'],
    cross: ['M01 Service Orders', 'M41 Purchase Orders', 'M19 General Ledger'],
    freg: {
      src: 124,
      sub: [
        ['1', 'Multi-Warehouse Bin Stock Tracking', 14],
        ['2', 'Real-Time Job Part Reservation', 12],
        ['3', 'Automated Reorder Point Triggers', 10],
        ['4', 'Cycle Counting & Stock Take Audits', 8]
      ]
    }
  },

  M41: {
    area: 'A06', code: 'M41', en: 'Warehouse Management', title: 'M41 · Warehouse Management',
    bn: 'ওয়্যারহাউস ব্যবস্থাপনা', icon: '🏭',
    desc: 'Physical execution — bins & slots, directed put-away, wave picking, packing, RF mobile, task interleaving.',
    kpis: [{ l: 'Active Purchase Orders' }, { l: 'On-Time Supplier Delivery' }],
    groups: [
      { en: 'Procurement', screens: [{ id: 'M41-orders', en: 'Purchase Orders Register', bn: 'পারচেজ অর্ডার রেজিস্টার', t: 'g' }] }
    ],
    reports: ['Supplier Lead Time Performance'], forms: ['Generate Purchase Order'], cross: ['M15 Inventory', 'M16 Suppliers'],
    freg: { src: 96, sub: [['1', 'Consumption-Driven Reorder Engine', 12], ['2', '3-Way Match & PO Approvals', 10]] }
  },

  M16: {
    area: 'A06', code: 'M16', en: 'Procurement & Sourcing', title: 'M16 · Procurement & Sourcing',
    bn: 'ক্রয় ও সোর্সিং', icon: '🛍️',
    desc: 'Demand-to-PO, RFQ with normalised comparison, three-way match, blanket orders, expediting, spend analysis.',
    kpis: [{ l: 'Active Suppliers' }, { l: 'Defective Parts Rate' }],
    groups: [
      { en: 'Suppliers', screens: [{ id: 'M16-vendors', en: 'Approved Vendor List (AVL)', bn: 'অনুমোদিত ভেন্ডর তালিকা', t: 'g' }] }
    ],
    reports: ['Supplier Quality Scorecards'], forms: ['Onboard New Vendor Form'], cross: ['M41 Purchase Orders', 'M44 Parts RMA'],
    freg: { src: 86, sub: [['1', 'Vendor Scorecard & SLA Engine', 10], ['2', 'Defective RMA Return Tracking', 8]] }
  },

  M42: {
    area: 'A06', code: 'M42', en: 'Supplier Relationship', title: 'M42 · Supplier Relationship',
    bn: 'সরবরাহকারী সম্পর্ক', icon: '🧑‍💼',
    desc: 'Supplier qualification gate, scorecards, corrective actions, risk assessment, compliance screening.',
    kpis: [{ l: 'Orders Picked Today' }],
    groups: [
      { en: 'Warehouse Floor', screens: [{ id: 'M42-docks', en: 'Dock Receiving & Inbound Shipments', bn: 'ডক রিসিভিং ও ইনবাউন্ড', t: 'g' }] }
    ],
    reports: ['Warehouse Picking Accuracy'], forms: ['Inbound GRN Receiving Form'], cross: ['M15 Inventory'],
    freg: { src: 84, sub: [['1', 'Wave Picking & Staging', 10], ['2', 'Barcode Inbound Receipt', 8]] }
  },

  M43: {
    area: 'A06', code: 'M43', en: 'Demand Planning', title: 'M43 · Demand Planning',
    bn: 'চাহিদা পরিকল্পনা', icon: '📈',
    desc: 'Forecast orchestration with MAPE tracking, safety stock, reorder policies, multi-echelon rebalancing.',
    kpis: [{ l: 'Transfers in Transit' }],
    groups: [
      { en: 'Inter-Branch', screens: [{ id: 'M43-transfers', en: 'Inter-Branch Stock Transfers', bn: 'শাখা স্টক স্থানান্তর', t: 'g' }] }
    ],
    reports: ['Transit Discrepancy Log'], forms: ['Create Inter-Branch Transfer'], cross: ['M15 Inventory', 'M04 Logistics'],
    freg: { src: 78, sub: [['1', 'Stock Transfer Manifest Generator', 10], ['2', 'Destination Seal Verification', 8]] }
  },

  M44: {
    area: 'A06', code: 'M44', en: 'Import & Trade Compliance', title: 'M44 · Import & Trade Compliance',
    bn: 'আমদানি ও বাণিজ্য', icon: '🚢',
    desc: 'LC/TT lifecycle, HS classification, ASYCUDA Bill of Entry, duty cascade, landed-cost allocation.',
    kpis: [{ l: 'Quarantined Items' }],
    groups: [
      { en: 'Quarantine', screens: [{ id: 'M44-quarantine', en: 'Quarantine Stock Bins', bn: 'কোয়ারেন্টাইন স্টক বিন', t: 'g' }] }
    ],
    reports: ['RMA Recovery Rate'], forms: ['Quarantine Inspection Form'], cross: ['M16 Suppliers', 'M15 Inventory'],
    freg: { src: 72, sub: [['1', 'Defective Part Quarantine Isolation', 8], ['2', 'Supplier RMA Return Workflow', 8]] }
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
  /* Rebuilt 2026-10-24 as a faithful mirror of contracts/nav/registry.json
   * (the canonical A08 structure): full groups/screens/reports/forms/freg per
   * module, cross-links that resolve to real module names. kpis carry an
   * optional `m` metric key served by /p03/finance/kpis (real Odoo reads). */
  M19: {
    area: 'A08', code: 'M19', en: 'Financial Accounting & GL', title: 'M19 · Financial Accounting & GL',
    bn: 'আর্থিক হিসাব', icon: '💰',
    desc: 'Chart of accounts, 7-dimension model, subledger posting engine, July–June close, statutory statements.',
    kpis: [
      { l: 'Revenue MTD', m: 'revenue_mtd' },
      { l: 'Gross Margin' },
      { l: 'Close Progress', m: 'open_period_closes' },
      { l: 'Unposted Subledgers' },
      { l: 'TB Imbalance', m: 'tb_imbalance' },
      { l: 'Journals MTD', m: 'posted_moves_mtd' },
      { l: 'Drafts in Review', m: 'draft_journals' }
    ],
    groups: [
      { en: 'Ledger', screens: [
        { id: 'M19-coa', en: 'Chart of Accounts', bn: 'হিসাবের ছক', t: 'g' },
        { id: 'M19-journals', en: 'Journals', bn: 'জার্নাল', t: 'g' },
        { id: 'M19-je', en: 'Journal Entry', bn: 'জার্নাল এন্ট্রি', t: 'f' },
        { id: 'M19-tb', en: 'Trial Balance', bn: 'ট্রায়াল ব্যালেন্স', t: 'r' },
        { id: 'M19-dimensions', en: '7-Dimension Model', bn: 'মাত্রা মডেল', t: 'g' }
      ]},
      { en: 'Close', screens: [
        { id: 'M19-close', en: 'Month-End Close Console', bn: 'মাসিক ক্লোজ', t: 'c' },
        { id: 'M19-periods', en: 'Periods & Locks', bn: 'পিরিয়ড', t: 'g' }
      ]},
      { en: 'Statements', screens: [
        { id: 'M19-bs', en: 'Balance Sheet', bn: 'উত্তরপত্র', t: 'r' },
        { id: 'M19-pl', en: 'Profit & Loss', bn: 'লাভ-ক্ষতি', t: 'r' },
        { id: 'M19-cf', en: 'Cash Flow', bn: 'নগদ প্রবাহ', t: 'r' },
        { id: 'M19-consol', en: 'Consolidation', bn: 'সমন্বয়', t: 'r' }
      ]},
      { en: 'Controls', screens: [
        { id: 'M19-suspense', en: 'Suspense & Control Accounts', bn: 'সাসপেন্স', t: 'g' },
        { id: 'M19-recon', en: 'Subledger vs Control', bn: 'উপ-খতিয়ান মিলকরণ', t: 'c' },
        { id: 'M19-audit', en: 'Immutable Audit Trail', bn: 'নিরবচ্ছিন্ন অডিট', t: 'g' }
      ]}
    ],
    reports: ['Trial Balance', 'P&L (BFRS)', 'Balance Sheet', 'Cash Flow', 'Dimensional P&L by Branch', 'Close Checklist Report'],
    forms: ['Journal Entry (manual/recurring)', 'Allocation Rule', 'Intercompany Charge'],
    cross: ['AR, Invoicing & Collections', 'AP & Employee Expense', 'Tax & Regulatory (BD)', 'Costing, Budget & FP&A'],
    freg: { src: 91, sub: [
      ['1', 'CoA & Dimensions', 12], ['2', 'Journals', 11], ['3', 'Subledger Posting Engine', 12],
      ['4', 'Fiscal Calendar & Close', 10], ['5', 'Multi-Entity & Consolidation', 9], ['6', 'Multi-Currency', 7],
      ['7', 'Statutory Statements', 9], ['8', 'Audit & Retention', 7], ['9', 'Accrual Framework', 8], ['10', 'Controls & SoD', 6]
    ] }
  },

  M20: {
    area: 'A08', code: 'M20', en: 'AR, Invoicing & Collections', title: 'M20 · AR, Invoicing & Collections',
    bn: 'প্রাপ্য ও ইনভয়েসিং', icon: '🧾',
    desc: 'Billable events from every module, Mushak 6.3 invoices, bKash/Nagad/card receipts, dunning, ageing.',
    kpis: [
      { l: 'Invoices MTD', m: 'ar_invoices_mtd' },
      { l: 'Overdue > 60d', m: 'overdue_gt_60d' },
      { l: 'DSO', m: 'dso' },
      { l: 'Auto-Gen %', m: 'auto_generated_pct' },
      { l: 'Within 1h %', m: 'within_1h_pct' },
      { l: 'Credit Notes', m: 'credit_notes_total' }
    ],
    groups: [
      { en: 'Invoicing', screens: [
        { id: 'M20-invoices', en: 'Customer Invoices', bn: 'গ্রাহক ইনভয়েস', t: 'g' },
        { id: 'M20-invoice', en: 'Invoice (Mushak 6.3)', bn: 'মুশক ৬.৩', t: 'f' },
        { id: 'M20-events', en: 'Billable Events', bn: 'বিলযোগ্য ঘটনা', t: 'g' },
        { id: 'M20-consolidated', en: 'Consolidated Corporate Invoices', bn: 'সমন্বিত ইনভয়েস', t: 'g' },
        { id: 'M20-brand', en: 'Brand Claim Invoices', bn: 'ব্র্যান্ড ইনভয়েস', t: 'g' }
      ]},
      { en: 'Receipts', screens: [
        { id: 'M20-receipts', en: 'Receipts (All Methods)', bn: 'রিসিট', t: 'g' },
        { id: 'M20-links', en: 'Payment Links', bn: 'পেমেন্ট লিংক', t: 'g' },
        { id: 'M20-allocation', en: 'Matching & Allocation', bn: 'মিলকরণ', t: 'c' }
      ]},
      { en: 'Credit Control', screens: [
        { id: 'M20-credit', en: 'Limits, Terms & Holds', bn: 'ক্রেডিট নিয়ন্ত্রণ', t: 'g' },
        { id: 'M20-dunning', en: 'Dunning Worklist', bn: 'দেনা আদায়', t: 'c' },
        { id: 'M20-disputes', en: 'Disputes', bn: 'বিরোধ', t: 'g' },
        { id: 'M20-refunds', en: 'Credit Notes & Refunds', bn: 'ক্রেডিট নোট', t: 'g' }
      ]},
      { en: 'Analysis', screens: [
        { id: 'M20-aging', en: 'AR Ageing', bn: 'বয়স্ক প্রাপ্য', t: 'r' },
        { id: 'M20-leakage', en: 'Revenue-Leakage Detection', bn: 'রাজস্ব ক্ষয়', t: 'r' },
        { id: 'M20-statements', en: 'Customer Statements', bn: 'গ্রাহক স্টেটমেন্ট', t: 'r' }
      ]}
    ],
    reports: ['AR Ageing by Segment', 'Dunning Effectiveness', 'Payment Method Mix', 'Invoice Accuracy', 'Brand Receivable Ageing', 'Collections Productivity'],
    forms: ['Invoice Request', 'Receipt', 'Credit Note', 'Refund', 'Payment Link'],
    cross: ['Financial Accounting & GL', 'Treasury & Banking', 'Tax & Regulatory (BD)'],
    freg: { src: 99, sub: [
      ['1', 'Billable-Event Intake', 12], ['2', 'Invoice Assembly', 12], ['3', 'Mushak 6.3 Rendering', 8],
      ['4', 'Delivery Channels', 6], ['5', 'Receipt Capture (8 methods)', 14], ['6', 'Matching & Allocation', 11],
      ['7', 'Credit Control', 9], ['8', 'Dunning & Collections', 12], ['9', 'Credit Notes & Refunds', 8], ['10', 'Leakage Detection', 7]
    ] }
  },

  M52: {
    area: 'A08', code: 'M52', en: 'AP & Employee Expense', title: 'M52 · AP & Employee Expense',
    bn: 'প্রদেয় ও ব্যয়', icon: '💸',
    desc: 'Vendor invoices with 3-way match, TDS/VDS at source, employee expenses & advances, payment runs.',
    kpis: [
      { l: 'Payables Open', m: 'vendor_bills_open' },
      { l: 'Match Exceptions', m: 'match_exceptions' },
      { l: 'Expense Claims Pending', m: 'expense_claims_pending' },
      { l: 'TDS MTD' }
    ],
    groups: [
      { en: 'Vendor Payables', screens: [
        { id: 'M52-bills', en: 'Vendor Bills', bn: 'বিক্রেতার বিল', t: 'g' },
        { id: 'M52-match', en: 'Match Exceptions', bn: 'মিল ব্যতিক্রম', t: 'g' },
        { id: 'M52-approval', en: 'Approval Workflow', bn: 'অনুমোদন', t: 'c' }
      ]},
      { en: 'Payments', screens: [
        { id: 'M52-runs', en: 'Payment Runs', bn: 'পেমেন্ট রান', t: 'c' },
        { id: 'M52-tds', en: 'TDS / VDS at Source', bn: 'উৎসে কর', t: 'g' },
        { id: 'M52-notes', en: 'Debit / Credit Notes', bn: 'ডেবিট নোট', t: 'g' }
      ]},
      { en: 'Employee Expense', screens: [
        { id: 'M52-claims', en: 'Expense Claims', bn: 'খরচের দাবি', t: 'g' },
        { id: 'M52-advances', en: 'Advances & Floats', bn: 'অগ্রিম', t: 'g' },
        { id: 'M52-perdiem', en: 'Per-Diem & Mileage', bn: 'ভাতা ও মাইলেজ', t: 'g' },
        { id: 'M52-policy', en: 'Expense Policy', bn: 'নীতি', t: 'g' }
      ]},
      { en: 'Analysis', screens: [
        { id: 'M52-aging', en: 'AP Ageing', bn: 'প্রদেয় বয়স', t: 'r' },
        { id: 'M52-grni', en: 'GRNI Accruals', bn: 'জিআরএনআই', t: 'r' }
      ]}
    ],
    reports: ['AP Ageing', 'TDS Deduction Register', 'Payment Run Summary', 'Expense by Category', 'GRNI Reconciliation', 'Duplicate Prevention Log'],
    forms: ['Vendor Bill', 'Expense Claim', 'Employee Advance', 'Debit Note'],
    cross: ['Procurement & Sourcing', 'Treasury & Banking', 'Tax & Regulatory (BD)'],
    freg: { src: 82, sub: [
      ['1', 'Invoice Capture', 10], ['2', 'Matching', 11], ['3', 'Approval', 8],
      ['4', 'Payable Ledger', 8], ['5', 'Payment Runs', 9], ['6', 'TDS/VDS', 9],
      ['7', 'Employee Expenses', 14], ['8', 'Advances & Cards', 8], ['9', 'GRNI', 5]
    ] }
  },

  M50: {
    area: 'A08', code: 'M50', en: 'Treasury & Banking', title: 'M50 · Treasury & Banking',
    bn: 'কোষাগার ও ব্যাংক', icon: '🏦',
    desc: 'Bank reconciliation, branch cash consolidation, rider COD, gateway/MFS settlement, BEFTN/RTGS execution.',
    kpis: [
      { l: 'Recon Exceptions', m: 'unreconciled_bank_lines' },
      { l: 'Auto-Match Rate', m: 'auto_match_rate' },
      { l: 'Cash Position' },
      { l: 'Branch Cash Uncollected' }
    ],
    groups: [
      { en: 'Cash', screens: [
        { id: 'M50-position', en: 'Consolidated Cash Position', bn: 'নগদ অবস্থান', t: 'd' },
        { id: 'M50-branchcash', en: 'Branch Cash Consolidation', bn: 'শাখা নগদ', t: 'c' },
        { id: 'M50-ridercod', en: 'Rider COD Settlement', bn: 'রাইডার সিওডি', t: 'c' },
        { id: 'M50-petty', en: 'Petty Cash (Imprest)', bn: 'খরচি নগদ', t: 'g' }
      ]},
      { en: 'Banking', screens: [
        { id: 'M50-accounts', en: 'Bank Account Master', bn: 'ব্যাংক হিসাব', t: 'g' },
        { id: 'M50-statements', en: 'Statements Import', bn: 'স্টেটমেন্ট', t: 'g' },
        { id: 'M50-recon', en: 'Auto Reconciliation', bn: 'স্বয়ংক্রিয় মিলকরণ', t: 'c' }
      ]},
      { en: 'Execution', screens: [
        { id: 'M50-beftn', en: 'BEFTN / RTGS Instructions', bn: 'বিইএফটিএন', t: 'g' },
        { id: 'M50-cheques', en: 'Cheque Management', bn: 'চেক', t: 'g' },
        { id: 'M50-mfs', en: 'MFS Disbursement', bn: 'এমএফএস বিতরণ', t: 'g' }
      ]},
      { en: 'Settlement', screens: [
        { id: 'M50-gateway', en: 'Gateway / MFS Settlement', bn: 'গেটওয়ে সেটেলমেন্ট', t: 'c' },
        { id: 'M50-cit', en: 'Cash-in-Transit', bn: 'নগদ পরিবহন', t: 'g' }
      ]},
      { en: 'Planning', screens: [
        { id: 'M50-forecast', en: 'Cash-Flow Forecast', bn: 'নগদ প্রবাহ পূর্বাভাস', t: 'r' },
        { id: 'M50-facilities', en: 'Facilities & Covenants', bn: 'সুবিধা ও চুক্তি', t: 'g' },
        { id: 'M50-fx', en: 'FX Holdings', bn: 'বৈদেশিক মুদ্রা', t: 'g' }
      ]}
    ],
    reports: ['Daily Cash Position', 'Bank Reconciliation Summary', 'Gateway Settlement Reconciliation', 'COD Settlement Report', '13-Week Cash Forecast', 'Bank Charges Analysis'],
    forms: ['Bank Statement Import', 'Payment Instruction', 'Cash Deposit', 'Imprest Top-Up'],
    cross: ['Financial Accounting & GL', 'AR, Invoicing & Collections', 'AP & Employee Expense'],
    freg: { src: 88, sub: [
      ['1', 'Bank Masters', 7], ['2', 'Statement & Recon', 13], ['3', 'Cash Position & Consolidation', 12],
      ['4', 'Payment Execution', 13], ['5', 'Gateway/MFS Settlement', 11], ['6', 'Forecasting', 8],
      ['7', 'Facilities & Trade Finance', 12], ['8', 'FX', 5], ['9', 'Controls', 7]
    ] }
  },

  M51: {
    area: 'A08', code: 'M51', en: 'Tax & Regulatory (BD)', title: 'M51 · Tax & Regulatory (BD)',
    bn: 'কর ও ভ্যাট', icon: '🏛️',
    desc: 'VAT 15%, Mushak 6.1–9.1 registers & returns, TDS/VDS, challans, NID capture, statutory calendar.',
    kpis: [
      { l: 'VAT Payable MTD', m: 'vat_collected_mtd' },
      { l: 'Mushak 9.1 Status', m: 'vat_returns_count' },
      { l: 'Input Credit Tracked', m: 'mushak_records' },
      { l: 'TDS Certificates Due' }
    ],
    groups: [
      { en: 'VAT', screens: [
        { id: 'M51-mushak61', en: 'Mushak 6.1 (Sales)', bn: 'মুশক ৬.১', t: 'g' },
        { id: 'M51-mushak62', en: 'Mushak 6.2 (Purchases)', bn: 'মুশক ৬.২', t: 'g' },
        { id: 'M51-mushak63', en: 'Mushak 6.3 Records', bn: 'মুশক ৬.৩', t: 'g' },
        { id: 'M51-vat91', en: 'VAT Return 9.1 Filing', bn: 'ভ্যাট রিটার্ন ৯.১', t: 'c' },
        { id: 'M51-challans', en: 'Challans (A-Challan)', bn: 'চালান', t: 'g' },
        { id: 'M51-input', en: 'Input Credit Tracking', bn: 'ইনপুট ক্রেডিট', t: 'g' }
      ]},
      { en: 'Withholding', screens: [
        { id: 'M51-tds', en: 'TDS Register', bn: 'টিডিএস রেজিস্টার', t: 'g' },
        { id: 'M51-vds', en: 'VDS (45 Services)', bn: 'ভিডিএস', t: 'g' },
        { id: 'M51-certs', en: 'Certificates', bn: 'সনদ', t: 'g' }
      ]},
      { en: 'Compliance', screens: [
        { id: 'M51-determination', en: 'Tax Determination Service', bn: 'কর নির্ধারণ', t: 'c' },
        { id: 'M51-nid', en: 'High-Value NID Capture', bn: 'এনআইডি সংগ্রহ', t: 'g' },
        { id: 'M51-calendar', en: 'Statutory Calendar', bn: 'বিধিবদ্ধ ক্যালেন্ডার', t: 'c' },
        { id: 'M51-audit', en: 'Audit Support Pack', bn: 'অডিট সহায়তা', t: 'r' }
      ]}
    ],
    reports: ['Mushak 9.1 Return Draft', 'VAT Reconciliation', 'TDS Annual Summary', 'SD & AT Liability', 'Marketplace VAT Model', 'Statutory Compliance Calendar'],
    forms: ['Mushak 6.3 Entry', 'TDS Entry', 'Challan', 'Tax Adjustment'],
    cross: ['AR, Invoicing & Collections', 'AP & Employee Expense', 'Financial Accounting & GL'],
    freg: { src: 78, sub: [
      ['1', 'Determination Service', 9], ['2', 'VAT Output/Input', 12], ['3', 'Mushak Registers', 11],
      ['4', 'VAT Return 9.1', 8], ['5', 'VDS', 7], ['6', 'TDS', 12],
      ['7', 'Challans & Certificates', 7], ['8', 'NID & Cash Controls', 4], ['9', 'Calendar & Audit', 8]
    ] }
  },

  M53: {
    area: 'A08', code: 'M53', en: 'Revenue Recognition & Settlement', title: 'M53 · Revenue Recognition & Settlement',
    bn: 'রাজস্ব ও নিষ্পত্তি', icon: '📊',
    desc: 'Performance obligations, contract balances, commission ledger, seller/partner payouts, clawbacks, escrow.',
    kpis: [
      { l: 'Commission Accrued', m: 'commission_accrued_count' },
      { l: 'Payout Runs MTD', m: 'payout_runs_open' },
      { l: 'Deferred Revenue', m: 'revenue_schedules_count' },
      { l: 'Recognised MTD' }
    ],
    groups: [
      { en: 'Revenue', screens: [
        { id: 'M53-obligations', en: 'Performance Obligations', bn: 'পারফরম্যান্স বাধ্যবাধকতা', t: 'g' },
        { id: 'M53-schedules', en: 'Revenue Schedules', bn: 'রাজস্ব সূচি', t: 'g' },
        { id: 'M53-contract', en: 'Contract Assets & Liabilities', bn: 'চুক্তি সম্পদ', t: 'r' }
      ]},
      { en: 'Commission', screens: [
        { id: 'M53-ledger', en: 'Commission Ledger', bn: 'কমিশন লেজার', t: 'g' },
        { id: 'M53-schemes', en: 'Incentive Schemes', bn: 'প্রণোদনা কর্মসূচি', t: 'g' }
      ]},
      { en: 'Settlements', screens: [
        { id: 'M53-payouts', en: 'Payout Runs', bn: 'পেআউট রান', t: 'c' },
        { id: 'M53-sellers', en: 'Seller Statements', bn: 'বিক্রেতা বিবৃতি', t: 'r' },
        { id: 'M53-partners', en: 'Partner / Referral Payouts', bn: 'পার্টনার পেআউট', t: 'g' },
        { id: 'M53-escrow', en: 'Escrow & Clawbacks', bn: 'এসক্রো', t: 'g' }
      ]}
    ],
    reports: ['Deferred Revenue Bridge', 'Rev-Rec by Stream', 'Commission Accrual', 'Payout Reconciliation', 'Clawback Register'],
    forms: ['Revenue Schedule', 'Payout Run', 'Clawback', 'Commission Scheme'],
    cross: ['Subscriptions & Recurring', 'Marketplace & Sellers', 'Partner & Channel'],
    freg: { src: 74, sub: [
      ['1', 'Performance Obligations', 10], ['2', 'Allocation & SSP', 8], ['3', 'Schedules & Triggers', 12],
      ['4', 'Modifications & Reversals', 8], ['5', 'Principal vs Agent', 5], ['6', 'Commission Ledger', 8],
      ['7', 'Seller Settlement', 10], ['8', 'Partner Payouts', 7], ['9', 'Escrow & Clawbacks', 6]
    ] }
  },

  M49: {
    area: 'A08', code: 'M49', en: 'Fixed Assets & Capex', title: 'M49 · Fixed Assets & Capex',
    bn: 'স্থায়ী সম্পদ ও ক্যাপেক্স', icon: '🏗️',
    desc: 'Capex requests to retirement — CWIP, dual-book depreciation (accounting + tax Third Schedule), verification.',
    kpis: [
      { l: 'Gross Block', m: 'assets_gross_block' },
      { l: 'CWIP', m: 'cwip_open_count' },
      { l: 'NBV' },
      { l: 'Depreciation Run' }
    ],
    groups: [
      { en: 'Capex', screens: [
        { id: 'M49-requests', en: 'Capex Requests', bn: 'ক্যাপেক্স অনুরোধ', t: 'g' },
        { id: 'M49-budget', en: 'Capital Budget', bn: 'মূলধনী বাজেট', t: 'g' }
      ]},
      { en: 'Register', screens: [
        { id: 'M49-register', en: 'Asset Register', bn: 'সম্পদ রেজিস্টার', t: 'g' },
        { id: 'M49-cwip', en: 'CWIP Tracking', bn: 'সিডব্লিউআইপি', t: 'g' },
        { id: 'M49-transfer', en: 'Transfers & Custodians', bn: 'স্থানান্তর', t: 'g' }
      ]},
      { en: 'Depreciation', screens: [
        { id: 'M49-dep', en: 'Dual-Book Depreciation', bn: 'দ্বৈত অবচয়', t: 'c' },
        { id: 'M49-schedules', en: 'Schedules & Movements', bn: 'সূচি', t: 'r' }
      ]},
      { en: 'Lifecycle', screens: [
        { id: 'M49-impairment', en: 'Revaluation & Impairment', bn: 'পুনর্মূল্যায়ন', t: 'g' },
        { id: 'M49-disposal', en: 'Disposal & Write-Off', bn: 'নিষ্পত্তি', t: 'g' },
        { id: 'M49-verify', en: 'Physical Verification', bn: 'শারীরিক যাচাই', t: 'c' }
      ]}
    ],
    reports: ['Fixed Asset Movement Schedule', 'Depreciation (Dual Book)', 'NBV by Category', 'Capex vs Budget', 'Disposal Gains/Losses'],
    forms: ['Capex Request', 'Asset Capitalisation', 'Transfer', 'Disposal'],
    cross: ['Financial Accounting & GL', 'Enterprise Assets & Test Equipment', 'Fleet & Vehicles'],
    freg: { src: 66, sub: [
      ['1', 'Capex & Approval', 9], ['2', 'Register & Capitalisation', 11], ['3', 'Componentisation', 5],
      ['4', 'Dual-Book Depreciation', 12], ['5', 'Revaluation & Impairment', 7], ['6', 'Transfers & Custody', 6],
      ['7', 'Verification & Tagging', 7], ['8', 'Disposal', 9]
    ] }
  },

  M54: {
    area: 'A08', code: 'M54', en: 'Costing, Budget & FP&A', title: 'M54 · Costing, Budget & FP&A',
    bn: 'ব্যয়, বাজেট ও এফপিএ', icon: '🧮',
    desc: 'Allocation cycles, job & contract costing, 14-stream business-line profitability, branch league, budgets.',
    kpis: [
      { l: 'Budget Variance', m: 'budget_total_variance' },
      { l: 'Branch League #1' },
      { l: 'Negative-Margin Branches' },
      { l: 'Job Costing Coverage' }
    ],
    groups: [
      { en: 'Costing', screens: [
        { id: 'M54-pools', en: 'Cost Pools & Elements', bn: 'ব্যয় পুল', t: 'g' },
        { id: 'M54-allocation', en: 'Allocation Cycles', bn: 'বণ্টন চক্র', t: 'c' },
        { id: 'M54-jobs', en: 'Job / Work-Order Costing', bn: 'কাজের ব্যয়', t: 'r' },
        { id: 'M54-loaded', en: 'Technician Loaded Cost', bn: 'কর্মী ব্যয়', t: 'r' }
      ]},
      { en: 'Profitability', screens: [
        { id: 'M54-streams', en: '14 Business-Line P&L', bn: '১৪ ব্যবসার লাভ', t: 'r' },
        { id: 'M54-branches', en: 'Branch Profitability', bn: 'শাখা লাভজনকতা', t: 'r' },
        { id: 'M54-customers', en: 'Customer Profitability', bn: 'গ্রাহক লাভজনকতা', t: 'r' },
        { id: 'M54-unitecon', en: 'Unit Economics', bn: 'একক অর্থনীতি', t: 'r' }
      ]},
      { en: 'Budgeting', screens: [
        { id: 'M54-budgets', en: 'Operating & Capital Budgets', bn: 'বাজেট', t: 'g' },
        { id: 'M54-workflow', en: 'Budget Workflow', bn: 'বাজেট প্রবাহ', t: 'c' },
        { id: 'M54-bva', en: 'Variance Analysis', bn: 'বিচ্যুতি বিশ্লেষণ', t: 'r' }
      ]},
      { en: 'Planning', screens: [
        { id: 'M54-rolling', en: 'Rolling Forecast', bn: 'রোলিং পূর্বাভাস', t: 'r' },
        { id: 'M54-scenario', en: 'Scenario Modelling', bn: 'পরিস্থিতি মডেল', t: 'c' },
        { id: 'M54-board', en: 'Board Pack', bn: 'বোর্ড প্যাক', t: 'r' }
      ]}
    ],
    reports: ['Business-Line P&L (14)', 'Branch League Table', 'Budget vs Actual', 'Job Margin Distribution', 'Customer Profitability Deciles', 'Unit Economics per Repair'],
    forms: ['Budget Version', 'Allocation Rule', 'Scenario'],
    cross: ['Financial Accounting & GL', 'Workshop & Depot Repair', 'Business Intelligence'],
    freg: { src: 70, sub: [
      ['1', 'Cost Model', 9], ['2', 'Allocation Cycles', 10], ['3', 'Job & Contract Costing', 11],
      ['4', 'Business-Line Profitability', 9], ['5', 'Branch & Channel Profitability', 8], ['6', 'Budgeting', 11],
      ['7', 'Variance & Forecast', 8], ['8', 'Board Pack', 4]
    ] }
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

/* =====================================================================
 * A08 live-surface map — registry screens backed by REAL Odoo models in
 * the g_finance addons (installed in fix_dev). The workspace opens these
 * as dynamic act_window views (list, or form for type-f screens). Every
 * screen NOT listed here keeps the honest "porting phase" empty state.
 * ===================================================================== */
export const P03_LIVE_SCREENS = {
  // M19 · Financial Accounting & GL (cd_gl_ext)
  'M19-coa': 'fix.chart.account',
  'M19-journals': 'account.move',
  'M19-je': 'account.move',
  'M19-dimensions': 'fix.journal.dimension',
  'M19-close': 'fix.period.close',
  'M19-periods': 'fix.period.close',
  // M20 · AR, Invoicing & Collections — all 15 screens moved to the
  // in-workspace data-screen framework (CD-M20-02); no stock doAction.
  // M50 · Treasury & Banking (cd_cash_position)
  // M51 · Tax & Regulatory BD (cd_tax_engine_bd)
  // M52 · AP & Employee Expense (cd_ap_ext)
  // M53 · Revenue Recognition & Settlement (cd_settlement_ext + cd_subscription)
  // M49 · Fixed Assets & Capex (cd_fixed_asset_ext)
  // M54 · Costing, Budget & FP&A (cd_fpa)
};

/* A08 module create surfaces: the "+ New" action for each finance module
 * opens the REAL model's form view (replaces the M01 service-order intake
 * that previously opened for every module). */
export const P03_MODULE_CREATE = {
  M19: { model: 'account.move', label: 'Journal Entry' },
  M20: { model: 'fix.ar.invoice', label: 'AR Invoice' },
  M52: { model: 'fix.vendor.invoice', label: 'Vendor Bill' },
  M50: { model: 'fix.payment.execution', label: 'Payment Instruction' },
  M51: { model: 'fix.mushak.register', label: 'Mushak 6.3 Entry' },
  M53: { model: 'fix.payout.run', label: 'Payout Run' },
  M49: { model: 'fix.fixed.asset', label: 'Fixed Asset' },
  M54: { model: 'fix.budget', label: 'Budget' },
};

/* A08 data-entry form chips → real model forms. Keyed `${moduleId}:${form
 * label}` (the same label can mean different models in different modules).
 * Unmapped chips fall back to the module create surface or an honest
 * "porting phase" toast — never the M01 intake form. */
export const P03_FORM_MODELS = {
  'M19:Journal Entry (manual/recurring)': 'account.move',
  'M19:Allocation Rule': 'fix.allocation.rule',
  'M20:Invoice Request': 'fix.ar.invoice',
  'M20:Credit Note': 'fix.credit.note',
  'M20:Refund': 'fix.credit.note',
  'M50:Bank Statement Import': 'fix.bank.statement.line',
  'M50:Payment Instruction': 'fix.payment.execution',
  'M51:Mushak 6.3 Entry': 'fix.mushak.register',
  'M51:TDS Entry': 'fix.tds.return',
  'M51:Challan': 'fix.tds.return',
  'M52:Vendor Bill': 'fix.vendor.invoice',
  'M52:Expense Claim': 'fix.expense.claim',
  'M53:Revenue Schedule': 'fix.revenue.schedule',
  'M53:Payout Run': 'fix.payout.run',
  'M49:Asset Capitalisation': 'fix.fixed.asset',
  'M54:Budget Version': 'fix.budget',
  'M54:Allocation Rule': 'fix.cost.allocation',
};

/* M19 in-workspace D365 screens (the GL pilot, 2026-10-24): every registry
 * screen of the Financial Accounting & GL module renders INSIDE the
 * workspace shell — fed by the /p03/gl/* endpoints — instead of leaving to
 * a stock Odoo backend view. `kind` selects the screen layout; `report`
 * parameterises the statement engine. Screens listed here are checked
 * BEFORE P03_LIVE_SCREENS. Extend to other modules one pilot at a time. */
export const P03_DATA_SCREENS = {
  // Ledger
  'M19-coa': { kind: 'coa' },
  'M19-journals': { kind: 'journals' },
  'M19-je': { kind: 'je_editor' },
  'M19-tb': { kind: 'statement', report: 'trial_balance' },
  'M19-dimensions': { kind: 'dimensions' },
  // Close
  'M19-close': { kind: 'close' },
  'M19-periods': { kind: 'periods' },
  // Statements
  'M19-bs': { kind: 'statement', report: 'balance_sheet' },
  'M19-pl': { kind: 'statement', report: 'pnl' },
  'M19-cf': { kind: 'statement', report: 'cash_flow' },
  'M19-consol': { kind: 'statement', report: 'consolidated' },
  // Controls
  'M19-suspense': { kind: 'suspense' },
  'M19-recon': { kind: 'recon' },
  'M19-audit': { kind: 'audit' },
  // ---- A08 completion (2026-10-25): generic model_list screens ----
  'M52-bills': { kind: 'model_list', model: 'fix.vendor.invoice',
    cols: ['vendor_id','invoice_ref','invoice_date','subtotal','tds_amount','total_payable','match_state'],
    stateField: 'match_state', actions: [{m:'action_request_payment',l:'Request Payment'}] },
  'M52-match': { kind: 'model_list', model: 'fix.vendor.invoice',
    cols: ['vendor_id','invoice_ref','invoice_date','total_payable','match_state','match_detail'],
    stateField: 'match_state', domain: [['match_state','!=','matched']] },
  'M52-claims': { kind: 'model_list', model: 'fix.expense.claim',
    cols: ['employee_id','description','expense_date','amount','state'],
    stateField: 'state', actions: [{m:'action_submit',l:'Submit'},{m:'action_approve',l:'Approve'}] },
  'M50-position': { kind: 'model_list', model: 'fix.cash.position',
    cols: ['as_of','bank_balance','drawer_float_total','pending_payments','total_position'] },
  'M50-statements': { kind: 'model_list', model: 'fix.bank.statement.line',
    cols: ['date','reference','narration','amount','match_state','matched_invoice_ref'],
    stateField: 'match_state' },
  'M50-recon': { kind: 'model_list', model: 'fix.bank.statement.line',
    cols: ['date','reference','narration','amount','match_state','matched_invoice_ref'],
    stateField: 'match_state', domain: [['match_state','=','unmatched']],
    actions: [{m:'auto_match',l:'Auto-Match'}] },
  'M50-beftn': { kind: 'model_list', model: 'fix.payment.execution',
    cols: ['source_model','source_id','payee','amount','method','state','executed_at'],
    stateField: 'state', actions: [{m:'action_execute',l:'Execute'}] },
  'M50-mfs': { kind: 'model_list', model: 'fix.payment.execution',
    cols: ['source_model','source_id','payee','amount','method','state','executed_at'],
    stateField: 'state', domain: [['method','!=','beftn']], actions: [{m:'action_execute',l:'Execute'}] },
  'M51-mushak61': { kind: 'model_list', model: 'fix.mushak.register',
    cols: ['mushak_no','invoice_ref','invoice_date','customer_name','taxable_amount','vat_amount','posted'] },
  'M51-mushak62': { kind: 'model_list', model: 'fix.mushak.register',
    cols: ['mushak_no','invoice_ref','invoice_date','supplier_name','taxable_amount','vat_amount','posted'] },
  'M51-mushak63': { kind: 'model_list', model: 'fix.mushak.register',
    cols: ['mushak_no','invoice_ref','invoice_date','customer_name','taxable_amount','vat_amount','total_payable','posted'],
    actions: [{m:'action_mark_posted',l:'Mark GL Posted'},{m:'action_rebuild_from_events',l:'Rebuild from Events'}] },
  'M51-vat91': { kind: 'model_list', model: 'fix.vat.return',
    cols: ['period','total_taxable','output_vat','input_vat','net_payable','due_date','state','filed_at'],
    stateField: 'state', actions: [{m:'action_prepare_period',l:'Prepare Period'},{m:'action_file',l:'File Return'}] },
  'M51-tds': { kind: 'model_list', model: 'fix.tds.return',
    cols: ['quarter','fiscal_year','total_withheld','deductor_count','due_date','state','filed_at'],
    stateField: 'state', actions: [{m:'action_prepare_quarter',l:'Prepare Quarter'},{m:'action_file',l:'File'}] },
  'M51-determination': { kind: 'model_list', model: 'fix.vat.treatment',
    cols: ['code','name','treatment_type','rate','active'] },
  'M51-certs': { kind: 'model_list', model: 'fix.withholding.certificate',
    cols: ['quarter','certificate_type','supplier_name','base_amount','rate_percent','withheld_amount','state'],
    stateField: 'state', actions: [{m:'action_issue',l:'Issue Certificate'}] },
  'M53-schedules': { kind: 'model_list', model: 'fix.revenue.schedule',
    cols: ['source_model','description','total_amount','recognized_amount','start_date','end_date','state'],
    stateField: 'state' },
  'M53-ledger': { kind: 'model_list', model: 'fix.commission.ledger',
    cols: ['name','seller_partner_id','gross_amount','commission_amount','tds_amount','net_payable','state'],
    stateField: 'state', actions: [{m:'action_post_to_gl',l:'Post Accrual to GL'}] },
  'M53-payouts': { kind: 'model_list', model: 'fix.payout.run',
    cols: ['name','period','total_gross','total_tds','total_payable','seller_count','state'],
    stateField: 'state', actions: [{m:'action_approve',l:'Approve (SoD)'},{m:'action_generate_beftn',l:'Generate BEFTN File'}] },
  'M53-sellers': { kind: 'model_list', model: 'fix.seller.statement',
    cols: ['seller_partner_id','period','gross_gmv','commission_amount','tds_withheld','net_payable','state'],
    stateField: 'state' },
  'M49-register': { kind: 'model_list', model: 'fix.fixed.asset',
    cols: ['name','category','gross','salvage','life_months','purchase_date','monthly_depreciation','state'],
    stateField: 'state', actions: [{m:'action_accrue_month',l:'Accrue Month'},{m:'action_dispose',l:'Dispose'}] },
  'M49-cwip': { kind: 'model_list', model: 'fix.cwip.entry',
    cols: ['name','amount','state','asset_id'],
    stateField: 'state', actions: [{m:'action_capitalise',l:'Capitalise'}] },
  'M54-budgets': { kind: 'model_list', model: 'fix.budget',
    cols: ['name','fiscal_year','planned_amount','actual_amount','variance','state'],
    stateField: 'state' },
  'M54-allocation': { kind: 'model_list', model: 'fix.cost.allocation',
    cols: ['name','direct_cost','allocated_overhead','total_cost'] },
  // ---- M20 · AR, Invoicing & Collections (CD-M20-02) — /p03/ar/* ----
  // Invoicing
  'M20-invoices': { kind: 'ar_invoices' },
  'M20-invoice': { kind: 'ar_editor' },
  'M20-events': { kind: 'ar_events' },
  'M20-consolidated': { kind: 'ar_consolidated' },
  'M20-brand': { kind: 'ar_brand' },
  // Receipts
  'M20-receipts': { kind: 'ar_receipts' },
  'M20-links': { kind: 'ar_links' },
  'M20-allocation': { kind: 'ar_allocation' },
  // Credit Control
  'M20-credit': { kind: 'ar_credit' },
  'M20-dunning': { kind: 'ar_dunning' },
  'M20-disputes': { kind: 'ar_disputes' },
  'M20-refunds': { kind: 'ar_refunds' },
  // Analysis
  'M20-aging': { kind: 'ar_aging' },
  'M20-leakage': { kind: 'ar_leakage' },
  'M20-statements': { kind: 'ar_statements' },
};

/* Built-in report chips → the in-workspace screen that already shows that
 * report's data (M19/M20 wired; other modules get an honest toast). Keyed
 * `${moduleId}:${reportName}`. */
export const P03_REPORT_ROUTES = {
  "M19:Trial Balance": "M19-tb",
  "M19:P&L (BFRS)": "M19-pl",
  "M19:Balance Sheet": "M19-bs",
  "M19:Cash Flow": "M19-cf",
  "M19:Dimensional P&L by Branch": "M19-dimensions",
  "M19:Close Checklist Report": "M19-close",
  "M20:AR Ageing by Segment": "M20-aging",
  "M20:Dunning Effectiveness": "M20-dunning",
  "M20:Payment Method Mix": "M20-receipts",
  "M20:Invoice Accuracy": "M20-refunds",
  "M20:Brand Receivable Ageing": "M20-brand",
  "M20:Collections Productivity": "M20-dunning",
};

Object.assign(P03_REPORT_ROUTES, {
  "M52:AP Ageing": "M52-bills",
  "M52:TDS Deduction Register": "M52-bills",
  "M52:Payment Run Summary": "M52-bills",
  "M52:Expense by Category": "M52-claims",
  "M52:GRNI Reconciliation": "M52-match",
  "M52:Duplicate Prevention Log": "M52-match",
  "M50:Daily Cash Position": "M50-position",
  "M50:Bank Reconciliation Summary": "M50-recon",
  "M50:Gateway Settlement Reconciliation": "M50-mfs",
  "M50:COD Settlement Report": "M50-mfs",
  "M51:Mushak 9.1 Return Draft": "M51-vat91",
  "M51:VAT Reconciliation": "M51-vat91",
  "M51:TDS Annual Summary": "M51-tds",
  "M53:Commission Accrual": "M53-ledger",
  "M53:Payout Reconciliation": "M53-payouts",
  "M53:Deferred Revenue Bridge": "M53-schedules",
  "M53:Rev-Rec by Stream": "M53-schedules",
  "M53:Clawback Register": "M53-sellers",
  "M49:Fixed Asset Movement Schedule": "M49-register",
  "M49:Depreciation (Dual Book)": "M49-register",
  "M49:NBV by Category": "M49-register",
  "M49:Capex vs Budget": "M49-cwip",
  "M49:Disposal Gains/Losses": "M49-register",
  "M54:Budget vs Actual": "M54-budgets",
});
