/* =====================================================================
   1000 FiX ERP — NAV DATA part 2 of 3: Categories C, D & E
   (Commercial & Revenue · Circular Economy · Supply Chain & Inventory)
   ===================================================================== */
window.FX_MODULES && (function () {

/* ============ A04 · COMMERCIAL, PRICING & REVENUE =================== */

/* ---------------- M37 PRODUCT & SERVICE CATALOGUE ------------------- */
window.FX_MODULES.M37 = { area:'A04', en:'Product & Service Catalogue', bn:'পণ্য ও সেবা ক্যাটালগ', icon:'🧾', rail:'commercial',
  desc:'Everything sellable — unified item master, rBOM, standard repair time, fault taxonomy, 14 contract families.',
  kpis:[ {l:'Active Items',v:'18,412',spark:[16200,16800,17300,17700,18000,18200,18412]},
          {l:'rBOM Coverage',v:'84.6%',st:'ok',spark:[70,73,76,79,81,83,84.6]},
          {l:'New SKUs MTD',v:'642',st:'info'},
          {l:'Pending Approval',v:'38',st:'warn'},
          {l:'Model Compatibility',v:'98.2%',st:'ok'},
          {l:'Bilingual Content',v:'96.8%',st:'ok'} ],
  groups:[
    {en:'Item Master', screens:[
      {id:'M37-items', en:'Unified Item Master', bn:'আইটেম মাস্টার', t:'g'},
      {id:'M37-item', en:'Item Record', bn:'আইটেম নথি', t:'f'},
      {id:'M37-taxonomy', en:'Typed Taxonomy (14 streams)', bn:'ট্যাক্সোনমি', t:'g'},
      {id:'M37-hierarchy', en:'Product Hierarchy', bn:'পণ্য স্তর', t:'g'} ]},
    {en:'Service Definitions', screens:[
      {id:'M37-services', en:'Service Definitions', bn:'সেবা সংজ্ঞা', t:'g'},
      {id:'M37-rbom', en:'Repair BOM (rBOM)', bn:'মেরামত বিওএম', t:'g'},
      {id:'M37-srt', en:'Standard Repair Time (SRT)', bn:'স্ট্যান্ডার্ড সময়', t:'g'},
      {id:'M37-kits', en:'Kits & Bundles', bn:'কিট ও বান্ডেল', t:'g'} ]},
    {en:'Compatibility & Faults', screens:[
      {id:'M37-brandmodel', en:'Brand-Model-Device Master', bn:'ব্র্যান্ড-মডেল', t:'g'},
      {id:'M37-fault', en:'Fault / Symptom / Root-Cause', bn:'ত্রুটি ট্যাক্সোনমি', t:'g'},
      {id:'M37-parts-id', en:'Part Identity & Supersession', bn:'পার্টস আইডেন্টিটি', t:'g'} ]},
    {en:'Plans & Templates', screens:[
      {id:'M37-contract-tpl', en:'14 Contract Families', bn:'চুক্তি টেমপ্লেট', t:'g'},
      {id:'M37-protection', en:'7 Protection Families', bn:'সুরক্ষা পরিকল্পনা', t:'g'},
      {id:'M37-rental-sku', en:'Rental SKUs & Grades', bn:'ভাড়া স্কু', t:'g'} ]},
    {en:'Governance', screens:[
      {id:'M37-approval', en:'Item Approval Workflow', bn:'অনুমোদন', t:'c'},
      {id:'M37-lifecycle', en:'Item Lifecycle & Deprecation', bn:'জীবনচক্র', t:'g'},
      {id:'M37-publication', en:'Channel Publication', bn:'চ্যানেল প্রকাশনা', t:'g'} ]} ],
  reports:['Catalogue Coverage by Brand','rBOM Completeness','SRT Calibration Variance','Item Margin Analysis','Deprecated Items Register','Bilingual Content Gaps'],
  forms:['Catalogue Item (9 types)','Service Definition','rBOM Line','Fault Code','Protection Product Template'],
  cross:['M11 price books','M36 quote build-up','M15 part compatibility','M38 storefront','M08 contract templates'],
  freg:{ src:120, sub:[
    ['1','Unified Item Master',14],['2','Typed Taxonomy',6],['3','Service Definition',11],
    ['4','rBOM & SRT',12],['5','Repair Operations',8],['6','Kits & Bundles',6],
    ['7','Product Hierarchy & Variants',8],['8','Brand-Model-Device Master',9],
    ['9','Fault Taxonomy',10],['10','Part Identity',9],['11','Contract & Protection Templates',10],
    ['12','Tax & Rev-Rec Classification',7],['13','Lifecycle & Governance',10] ] } };

/* ---------------- M11 PRICING & RATE CARDS --------------------------- */
window.FX_MODULES.M11 = { area:'A04', en:'Pricing & Rate Cards', bn:'মূল্য ও রেট কার্ড', icon:'🏷️', rail:'commercial',
  desc:'Price engine (item×customer×channel×date), labour rate cards, brand reimbursement rates, discount governance.',
  kpis:[ {l:'Realised Margin',v:'42.8%',d:'+1.6pt',up:1,st:'ok',spark:[38,39,40,41,41.8,42.3,42.8]},
          {l:'Discount Leaks MTD',v:'৳ 41 K',d:'−38%',up:1,st:'ok'},
          {l:'Rate Cards Live',v:'46',st:'info'},
          {l:'Brand Reimb. Rates',v:'17',st:'ok'},
          {l:'Simulations MTD',v:'212',st:'info'},
          {l:'Margin Floors Breached',v:'0',st:'ok'} ],
  groups:[
    {en:'Price Books', screens:[
      {id:'M11-books', en:'Price Books', bn:'প্রাইস বুক', t:'g'},
      {id:'M11-engine', en:'Price Resolution Engine', bn:'মূল্য ইঞ্জিন', t:'c'},
      {id:'M11-versions', en:'Versioning & Mass Changes', bn:'সংস্করণ', t:'g'} ]},
    {en:'Rate Cards', screens:[
      {id:'M11-labour', en:'Labour Rate Cards', bn:'শ্রম রেট কার্ড', t:'g'},
      {id:'M11-parts', en:'Parts Pricing Rules', bn:'পার্টস মূল্য', t:'g'},
      {id:'M11-brand', en:'Brand Reimbursement Rates', bn:'ব্র্যান্ড হার', t:'g'},
      {id:'M11-adjust', en:'Adjustment Rules', bn:'সমন্বয় নিয়ম', t:'g'} ]},
    {en:'Governance', screens:[
      {id:'M11-discounts', en:'Discount Governance', bn:'ছাড় নিয়ন্ত্রণ', t:'c'},
      {id:'M11-floors', en:'Cost-Plus & Margin Floors', bn:'মার্জিন ফ্লোর', t:'g'},
      {id:'M11-promos', en:'Promotions', bn:'প্রোমোশন', t:'g'} ]},
    {en:'Analytics', screens:[
      {id:'M11-simulate', en:'Price Simulation', bn:'মূল্য সিমুলেশন', t:'c'},
      {id:'M11-realised', en:'Realised-Price Analytics', bn:'বাস্তব মূল্য', t:'r'} ]} ],
  reports:['Realised Price vs Card','Discount Register by Approver','Rate-Card Utilisation','Margin by Service Line','Promotion Effectiveness','Brand Reimbursement Recovery'],
  forms:['Price Book','Rate Card','Discount Policy','Promotion','Price Simulation Request'],
  cross:['M37 catalogue items','M36 quotation lock','M54 margin analytics','M09 brand claim rates'],
  freg:{ src:97, sub:[
    ['1','Pricing Engine',12],['2','Price Books',10],['3','Rate Cards',11],
    ['4','Parts Pricing',9],['5','Customer/Contract Pricing',8],['6','Brand Reimbursement',7],
    ['7','Discount Governance',10],['8','Promotions',7],['9','Adjustment Rules',8],
    ['10','Simulation & Trace',7],['11','Versioning & Approval',8] ] } };

/* ---------------- M36 QUOTATION, ESTIMATION & TENDER ------------------ */
window.FX_MODULES.M36 = { area:'A04', en:'Quotations & Tenders', bn:'কোটেশন ও টেন্ডার', icon:'📄', rail:'commercial',
  desc:'Estimate build-up to customer quotation, multi-channel approval loop, e-signature, tender & competitive bids.',
  kpis:[ {l:'Quotes Open',v:'184',st:'info',spark:[160,166,172,176,180,182,184]},
          {l:'Conversion',v:'78.4%',d:'+2.1pt',up:1,st:'ok'},
          {l:'Awaiting Customer',v:'96',st:'warn'},
          {l:'Avg Turnaround',v:'4.2 h',d:'−36 min',up:1,st:'ok'},
          {l:'Tenders Live',v:'6',st:'info'},
          {l:'Declined → Diagnostic Fee',v:'৳ 84 K MTD',st:'info'} ],
  groups:[
    {en:'Estimates', screens:[
      {id:'M36-estimates', en:'Internal Estimates', bn:'অভ্যন্তরীণ অনুমান', t:'g'},
      {id:'M36-buildup', en:'Build-Up Workbench', bn:'বিল্ড-আপ ওয়ার্কবেঞ্চ', t:'f'} ]},
    {en:'Quotations', screens:[
      {id:'M36-quotes', en:'Customer Quotations', bn:'গ্রাহক কোটেশন', t:'g'},
      {id:'M36-record', en:'Quotation Record', bn:'কোটেশন নথি', t:'f'},
      {id:'M36-versions', en:'Versions & Counter-Offer', bn:'সংস্করণ', t:'g'},
      {id:'M36-esign', en:'e-Signature & Evidence', bn:'ই-স্বাক্ষর', t:'g'} ]},
    {en:'Approval Loop', screens:[
      {id:'M36-loop', en:'Customer Approval Loop', bn:'গ্রাহক অনুমোদন', t:'c'},
      {id:'M36-internal', en:'Internal Approval Routing', bn:'অভ্যন্তরীণ অনুমোদন', t:'g'},
      {id:'M36-declined', en:'Declined-Repair Handling', bn:'প্রত্যাখ্যাত মেরামত', t:'g'} ]},
    {en:'Tenders', screens:[
      {id:'M36-tenders', en:'Tenders & Bids', bn:'টেন্ডার', t:'g'},
      {id:'M36-compliance', en:'Compliance Matrix', bn:'কমপ্লায়েন্স ম্যাট্রিক্স', t:'f'},
      {id:'M36-bonds', en:'Bid Bonds', bn:'বিড বন্ড', t:'g'} ]} ],
  reports:['Quote Conversion by Channel','Approval Cycle Time','Decline Reasons Pareto','Tender Win/Loss','Margin on Approved Quotes'],
  forms:['Estimate','Quotation (versioned)','Tender Bid','Counter-Offer'],
  cross:['M37 + M11 build-up','M01 estimate approval','M24 e-signature envelopes','M08 contract conversion'],
  freg:{ src:86, sub:[
    ['1','Estimate Build-Up',10],['2','Quotation Object',12],['3','Versioning',7],
    ['4','Approval Routing',9],['5','Customer Approval Loop (8 channels)',13],['6','Partial Accept & Counter',6],
    ['7','e-Signature',6],['8','Declined Handling',6],['9','Tender & Bid',9],['10','Templates & Bilingual Gen',8] ] } };

/* ---------------- M08 CONTRACT LIFECYCLE -------------------------------- */
window.FX_MODULES.M08 = { area:'A04', en:'Contract Lifecycle (AMC)', bn:'চুক্তি ব্যবস্থাপনা', icon:'📑', rail:'commercial',
  desc:'14 contract families — entitlement definition/consumption, PM schedules, SLA credits, amendments, renewals.',
  kpis:[ {l:'Active Contracts',v:'2,148',spark:[1840,1920,1990,2050,2090,2120,2148]},
          {l:'Contract Base Value',v:'৳ 24.6 Cr',d:'+11%',up:1,spark:[18.2,19.4,20.6,21.8,22.9,23.8,24.6]},
          {l:'Renewal Rate',v:'84.2%',d:'+6pt',up:1,st:'ok',spark:[60,66,71,75,79,82,84.2]},
          {l:'Neg-Margin Contracts',v:'1.8%',st:'ok'},
          {l:'Entitlement Utilisation',v:'71.4%',st:'info'},
          {l:'PM Visits Due (7d)',v:'86',st:'warn'} ],
  groups:[
    {en:'Contract Register', screens:[
      {id:'M08-contracts', en:'Contracts', bn:'চুক্তি', t:'g'},
      {id:'M08-record', en:'Contract Record', bn:'চুক্তি নথি', t:'f'},
      {id:'M08-families', en:'14 Product Families', bn:'পরিবার', t:'g'},
      {id:'M08-master', en:'Master Agreements', bn:'মাস্টার চুক্তি', t:'g'} ]},
    {en:'Coverage & Entitlement', screens:[
      {id:'M08-scope', en:'Covered Assets & Sites', bn:'আওতাভুক্ত সম্পদ', t:'g'},
      {id:'M08-entitle', en:'Entitlement & Consumption', bn:'সুবিধা ব্যবহার', t:'g'},
      {id:'M08-balance', en:'Balances, Carry-Over, Top-Up', bn:'ব্যালান্স', t:'g'} ]},
    {en:'Service Commitments', screens:[
      {id:'M08-sla', en:'Contract SLA & Credits', bn:'এসএলএ ও ক্রেডিট', t:'g'},
      {id:'M08-pm', en:'PM & Calibration Schedules', bn:'পিএম সূচি', t:'g'},
      {id:'M08-auto-work', en:'Contract-Driven Work', bn:'চুক্তিভিত্তিক কাজ', t:'g'} ]},
    {en:'Change & Renewal', screens:[
      {id:'M08-amend', en:'Amendments & Variations', bn:'সংশোধনী', t:'g'},
      {id:'M08-renewals', en:'Renewals & Auto-Renew', bn:'নবায়ন', t:'c'},
      {id:'M08-termination', en:'Suspension / Termination', bn:'স্থগিত/অবসান', t:'g'},
      {id:'M08-churn', en:'Churn & Win-Back', bn:'চার্ন ও পুনরুদ্ধার', t:'r'} ]},
    {en:'Financials', screens:[
      {id:'M08-pricing', en:'Contract Pricing Link', bn:'চুক্তি মূল্য', t:'g'},
      {id:'M08-profit', en:'Profitability & Alerts', bn:'লাভজনকতা', t:'r'} ]} ],
  reports:['Contract Base Movement','Entitlement Consumption by Client','SLA Credit Register','PM Compliance Report','Renewal Pipeline & Risk','Contract P&L'],
  forms:['Contract (14 families)','Amendment','Asset Attach/Detach','Renewal Quote','PM Schedule'],
  cross:['M01 entitlement check','M11 contract pricing','M39 recurring billing','M67 implementation projects','P04 corporate portal'],
  freg:{ src:108, sub:[
    ['1','Template-Driven Creation',12],['2','Parties & Approval',8],['3','Coverage Scope',10],
    ['4','Entitlement Engine',14],['5','SLA & Service Credits',10],['6','PM Schedules',9],
    ['7','Amendments',8],['8','Renewal Governance',9],['9','Churn & Win-Back',6],
    ['10','Pricing & Profitability',10],['11','Documents & Signature',7],['12','Obligation Calendar',5] ] } };

/* ---------------- M09 WARRANTY, PROTECTION & CLAIMS ---------------------- */
window.FX_MODULES.M09 = { area:'A04', en:'Warranty & Claims', bn:'ওয়ারেন্টি ও ক্লেইম', icon:'🛡️', rail:'commercial',
  desc:'Warranty register, entitlement "who pays", brand claims with auto evidence packs, recalls, protection plans.',
  kpis:[ {l:'Claims Submitted MTD',v:'1,842',st:'info',spark:[1420,1520,1610,1690,1750,1800,1842]},
          {l:'First-Submission Approval',v:'92.4%',st:'ok',spark:[84,86,88,89,90,91,92.4]},
          {l:'Reimbursement Days',v:'38 d',d:'−14 d',up:1,st:'ok',spark:[62,56,51,47,43,40,38]},
          {l:'Revenue Leakage',v:'1.8%',d:'−13pt',up:1,st:'ok',spark:[15,12,9,7,5,3,1.8]},
          {l:'Claims < 72h',v:'94.2%',st:'ok'},
          {l:'Appeals Open',v:'18',st:'warn'} ],
  groups:[
    {en:'Warranty Register', screens:[
      {id:'M09-register', en:'Warranty Register', bn:'ওয়ারেন্টি রেজিস্টার', t:'g'},
      {id:'M09-validate', en:'Manufacturer Validation', bn:'প্রস্তুতকারক যাচাই', t:'g'},
      {id:'M09-repair-wty', en:'Repair Warranty & Rework', bn:'মেরামত ওয়ারেন্টি', t:'g'},
      {id:'M09-transfer', en:'Transfer & Void Rules', bn:'হস্তান্তর নিয়ম', t:'g'} ]},
    {en:'Brand Claims', screens:[
      {id:'M09-claims', en:'Brand Claims', bn:'ব্র্যান্ড ক্লেইম', t:'g'},
      {id:'M09-record', en:'Claim Record', bn:'ক্লেইম নথি', t:'f'},
      {id:'M09-evidence', en:'Evidence Assembly', bn:'প্রমাণ সংগ্রহ', t:'c'},
      {id:'M09-brandrules', en:'Brand Rules & Formats', bn:'ব্র্যান্ড নিয়ম', t:'g'},
      {id:'M09-recon', en:'Brand Reconciliation', bn:'ব্র্যান্ড মিলকরণ', t:'c'} ]},
    {en:'Protection Plans', screens:[
      {id:'M09-protection', en:'7 Protection Families', bn:'সুরক্ষা পরিকল্পনা', t:'g'},
      {id:'M09-policies', en:'Policy Lifecycle', bn:'পলিসি জীবনচক্র', t:'g'},
      {id:'M09-reserves', en:'Reserves & Loss Ratio', bn:'রিজার্ভ ও লস রেশিও', t:'r'} ]},
    {en:'Recalls & Fraud', screens:[
      {id:'M09-recalls', en:'Recalls & Campaigns', bn:'রিকল ক্যাম্পেইন', t:'g'},
      {id:'M09-fraud', en:'Fraud Detection', bn:'প্রতারণা শনাক্তকরণ', t:'g'} ]} ],
  reports:['Claim Ageing by Brand','Reimbursement Cycle Time','Claim Rejection Analysis','Evidence Completeness','Loss Ratio by Product','Recall Coverage Report'],
  forms:['Brand Claim','Protection Policy','Claim Appeal','Recall Campaign'],
  cross:['M01 warranty orders','M17 evidence from asset history','M20 claim receivables','P08 brand partner portal'],
  freg:{ src:108, sub:[
    ['1','Warranty Register',12],['2','Manufacturer Validation',8],['3','Repair Warranty',8],
    ['4','Entitlement Evaluation',9],['5','Protection Products',13],['6','Claim Assessment',9],
    ['7','Evidence Assembly',9],['8','Brand Submission',10],['9','Decisions & Appeals',9],
    ['10','Reconciliation',8],['11','Recalls',7],['12','Fraud Detection',6] ] } },

/* ---------------- M39 SUBSCRIPTION & RECURRING --------------------------- */
window.FX_MODULES.M39 = { area:'A04', en:'Subscriptions & Recurring', bn:'সাবস্ক্রিপশন', icon:'🔄', rail:'commercial',
  desc:'Zuora-class billing — schedules, usage rating, proration, dunning, MRR/ARR/churn/NRR metrics.',
  kpis:[ {l:'MRR',v:'৳ 1.84 Cr',d:'+6.2%',up:1,spark:[1.42,1.48,1.54,1.61,1.68,1.76,1.84]},
          {l:'ARR',v:'৳ 22.1 Cr',d:'+9%',up:1},
          {l:'NRR',v:'112%',st:'ok',spark:[98,101,104,107,109,111,112]},
          {l:'Churn (Logo)',v:'4.1%',d:'−1.2pt',up:1,st:'ok'},
          {l:'Billing Exceptions',v:'12',st:'warn'},
          {l:'Dunning in Progress',v:'38',st:'warn'} ],
  groups:[
    {en:'Subscriptions', screens:[
      {id:'M39-subs', en:'Subscriptions', bn:'সাবস্ক্রিপশন', t:'g'},
      {id:'M39-record', en:'Subscription Record', bn:'সাবস্ক্রিপশন নথি', t:'f'},
      {id:'M39-plans', en:'Plan Changes', bn:'পরিকল্পনা পরিবর্তন', t:'g'} ]},
    {en:'Rating & Billing', screens:[
      {id:'M39-usage', en:'Usage Rating', bn:'ব্যবহার রেটিং', t:'g'},
      {id:'M39-runs', en:'Billing Runs', bn:'বিলিং রান', t:'c'},
      {id:'M39-proration', en:'Proration Engine', bn:'প্রোরেশন', t:'c'} ]},
    {en:'Payments', screens:[
      {id:'M39-autopay', en:'Autopay & Retry', bn:'অটোপে', t:'g'},
      {id:'M39-dunning', en:'Dunning Coordination', bn:'ডানিং', t:'g'} ]},
    {en:'Metrics', screens:[
      {id:'M39-mrr', en:'MRR Movement', bn:'এমআরআর', t:'d'},
      {id:'M39-cohorts', en:'Cohort Analysis', bn:'কোহোর্ট', t:'r'},
      {id:'M39-forecast', en:'Recurring Forecast', bn:'পুনরাবৃত্ত পূর্বাভাস', t:'r'} ]} ],
  reports:['MRR Waterfall','Churn & NRR Cohorts','Usage vs Committed','Billing Exception Log','Deferred Revenue Bridge'],
  forms:['Subscription','Billing Schedule','Plan Change','Dunning Step'],
  cross:['M08 contract sources','M20 invoices','M53 rev-rec','M50 autopay settlement'],
  freg:{ src:92, sub:[
    ['1','Subscription Object',10],['2','Billing Schedules',9],['3','Charge Models',10],
    ['4','Quantity & Proration',12],['5','Usage Rating',8],['6','Billing Runs',11],
    ['7','Credits & Adjustments',7],['8','Suspend / Cancel / Renew',9],['9','Autopay & Dunning',8],['10','Metrics & Forecast',8] ] } },

/* ---------------- M38 E-COMMERCE ------------------------------------------- */
window.FX_MODULES.M38 = { area:'A04', en:'E-Commerce Storefront', bn:'ই-কমার্স', icon:'🛒', rail:'commercial',
  desc:'Online storefront — compatibility filtering, mixed carts, service booking as commerce, bKash/Nagad/card checkout.',
  kpis:[ {l:'Orders MTD',v:'4,842',d:'+14%',up:1,spark:[3620,3820,4010,4200,4410,4620,4842]},
          {l:'Conversion',v:'3.8%',d:'+0.4pt',up:1,st:'ok'},
          {l:'Cart Abandon',v:'62%',st:'warn'},
          {l:'bKash Share',v:'41%',st:'info'},
          {l:'Refurb GMV MTD',v:'৳ 32.4 L',d:'+18%',up:1},
          {l:'RMA Rate',v:'1.6%',st:'ok'} ],
  groups:[
    {en:'Storefront', screens:[
      {id:'M38-storefront', en:'Storefront Preview', bn:'স্টোরফ্রন্ট', t:'d'},
      {id:'M38-merch', en:'Merchandising', bn:'মার্চেন্ডাইজিং', t:'g'},
      {id:'M38-compat', en:'Compatibility Filters', bn:'সামঞ্জস্য ফিল্টার', t:'g'} ]},
    {en:'Cart & Checkout', screens:[
      {id:'M38-carts', en:'Carts & Abandonment', bn:'কার্ট', t:'g'},
      {id:'M38-checkout', en:'Checkout & Payment Orchestration', bn:'চেকআউট', t:'c'},
      {id:'M38-delivery', en:'Delivery Options', bn:'ডেলিভারি অপশন', t:'g'} ]},
    {en:'Orders', screens:[
      {id:'M38-orders', en:'Online Orders', bn:'অনলাইন অর্ডার', t:'g'},
      {id:'M38-returns', en:'Returns & RMA', bn:'ফেরত ও আরএমএ', t:'g'},
      {id:'M38-stock', en:'Stock Exposure Policy', bn:'স্টক এক্সপোজার', t:'g'} ]},
    {en:'Commerce Marketing', screens:[
      {id:'M38-promos', en:'Checkout Promotions', bn:'প্রোমোশন', t:'g'},
      {id:'M38-recovery', en:'Abandoned-Cart Recovery', bn:'কার্ট পুনরুদ্ধার', t:'c'} ]} ],
  reports:['Funnel & Conversion','Payment Method Mix','Refurb GMV by Grade','Delivery Performance','RMA & Returns Report','Abandonment Recovery Rate'],
  forms:['Online Order','RMA Request','Storefront Slot','Delivery Slot'],
  cross:['M15 stock exposure','M10 points earn/redeem','M20 payment gateways','M14 refurb listings','M35 campaigns'],
  freg:{ src:92, sub:[
    ['1','Storefront & Browse',12],['2','Merchandising',7],['3','Cart',9],
    ['4','Checkout & Payments',14],['5','Online Orders',9],['6','Stock Exposure',6],
    ['7','Returns & RMA',9],['8','B2B Commerce',11],['9','Recovery & Analytics',9],['10','Service Booking Commerce',6] ] } },

/* ---------------- M12 MARKETPLACE ------------------------------------------ */
window.FX_MODULES.M12 = { area:'A04', en:'Marketplace & Sellers', bn:'মার্কেটপ্লেস', icon:'🌐', rail:'commercial',
  desc:'Freelance engineer / shop ecosystem — KYC, listings, job broadcast & bidding, commission, wallets, disputes.',
  kpis:[ {l:'Active Sellers',v:'418',spark:[240,280,316,346,372,396,418]},
          {l:'Job Fill Rate',v:'81.2%',st:'ok',spark:[62,67,71,74,77,79,81.2]},
          {l:'Marketplace Share',v:'18.4%',d:'+3pt',up:1},
          {l:'Disputes Open',v:'14',st:'warn'},
          {l:'Payouts MTD',v:'৳ 48.2 L',st:'info'},
          {l:'Seller NPS',v:'47',st:'ok'} ],
  groups:[
    {en:'Sellers', screens:[
      {id:'M12-sellers', en:'Seller Directory', bn:'বিক্রেতা তালিকা', t:'g'},
      {id:'M12-kyc', en:'KYC & Approval', bn:'কেওয়াইসি', t:'c'},
      {id:'M12-agreements', en:'Agreements & Tiers', bn:'চুক্তি ও স্তর', t:'g'} ]},
    {en:'Supply', screens:[
      {id:'M12-listings', en:'Listings & Moderation', bn:'লিস্টিং', t:'g'},
      {id:'M12-stock', en:'Seller Stock', bn:'বিক্রেতা স্টক', t:'g'},
      {id:'M12-training', en:'Standards & Training', bn:'মান ও প্রশিক্ষণ', t:'g'} ]},
    {en:'Job Market', screens:[
      {id:'M12-broadcast', en:'Job Broadcast', bn:'কাজ সম্প্রচার', t:'c'},
      {id:'M12-bids', en:'Bidding & Award', bn:'বিডিং ও পুরস্কার', t:'g'},
      {id:'M12-oversight', en:'Execution Oversight', bn:'কাজের তত্ত্বাবধান', t:'g'} ]},
    {en:'Money', screens:[
      {id:'M12-commission', en:'Commission Schemes', bn:'কমিশন', t:'g'},
      {id:'M12-wallet', en:'Seller Wallets & Payouts', bn:'ওয়ালেট ও পেআউট', t:'g'},
      {id:'M12-fees', en:'Fees & Promotion', bn:'ফি ও প্রমোশন', t:'g'} ]},
    {en:'Trust', screens:[
      {id:'M12-reviews', en:'Ratings & Reviews', bn:'রেটিং ও রিভিউ', t:'g'},
      {id:'M12-disputes', en:'Disputes & Mediation', bn:'বিরোধ', t:'c'},
      {id:'M12-trust', en:'Fraud & Trust Ops', bn:'বিশ্বাস ও প্রতারণা', t:'g'} ]} ],
  reports:['Supply-Demand Liquidity','Fill Rate & Time-to-Accept','Commission Revenue','Dispute Rate & Outcomes','Seller Scorecard Distribution'],
  forms:['Seller Application','Listing','Payout Run','Dispute Case'],
  cross:['M33 seller party','M01 marketplace orders','M53 commission settlement','P07 seller portal','M51 VAT model'],
  freg:{ src:101, sub:[
    ['1','Seller Registration & KYC',12],['2','Agreements & Tiers',7],['3','Listings',9],
    ['4','Job Broadcast & Bidding',14],['5','Execution Oversight',10],['6','Ratings',6],
    ['7','Performance Consequences',6],['8','Disputes',9],['9','Commission & Fees',10],
    ['10','Wallet & Payouts',10],['11','Trust & Safety',8] ] } },

/* ---------------- M40 PARTNER & CHANNEL ------------------------------------ */
window.FX_MODULES.M40 = { area:'A04', en:'Partner & Channel', bn:'পার্টনার ও চ্যানেল', icon:'🤝', rail:'commercial',
  desc:'Brand partnerships (17+), alliances, referral partners, deal registration, resellers, franchise management.',
  kpis:[ {l:'Brand Partners',v:'17',st:'ok'},
          {l:'Referral Partners',v:'348',d:'+42',up:1},
          {l:'Deal Registrations',v:'38',st:'info'},
          {l:'Partner Revenue MTD',v:'৳ 1.12 Cr',d:'+8%',up:1},
          {l:'Audits Due (90d)',v:'5',st:'warn'},
          {l:'Rebates Accrued',v:'৳ 6.4 L',st:'info'} ],
  groups:[
    {en:'Partner Master', screens:[
      {id:'M40-partners', en:'Partner Directory', bn:'পার্টনার তালিকা', t:'g'},
      {id:'M40-brand', en:'Brand Partner Relations', bn:'ব্র্যান্ড সম্পর্ক', t:'g'},
      {id:'M40-authorisation', en:'Authorisation & Certification', bn:'অনুমোদন', t:'g'} ]},
    {en:'Programmes', screens:[
      {id:'M40-alliance', en:'Alliance Benefits', bn:'জোট সুবিধা', t:'g'},
      {id:'M40-referral', en:'Referral Programme', bn:'রেফারেল কর্মসূচি', t:'g'},
      {id:'M40-dealreg', en:'Deal Registration', bn:'ডিল নিবন্ধন', t:'g'},
      {id:'M40-reseller', en:'Resellers', bn:'রিসেলার', t:'g'},
      {id:'M40-franchise', en:'Franchise Management', bn:'ফ্র্যাঞ্চাইজি', t:'g'} ]},
    {en:'Commercial', screens:[
      {id:'M40-rebates', en:'Rebates & MDF', bn:'রিবেট', t:'g'},
      {id:'M40-comarketing', en:'Co-Marketing', bn:'সহ-বিপণন', t:'g'},
      {id:'M40-conflict', en:'Channel Conflict', bn:'চ্যানেল দ্বন্দ্ব', t:'g'} ]},
    {en:'Performance', screens:[
      {id:'M40-health', en:'Health & Risk', bn:'স্বাস্থ্য ও ঝুঁকি', t:'r'},
      {id:'M40-ranking', en:'Ranking & Scorecards', bn:'র‍্যাংকিং', t:'r'} ]} ],
  reports:['Partner Revenue Contribution','Referral Conversion','Brand Audit Calendar','Rebate Accruals','Channel Conflict Log'],
  forms:['Partner','Deal Registration','Rebate Scheme','Franchise Agreement'],
  cross:['M42 supplier class brands','M09 brand claims','M53 rebates','P12 partner portal'],
  freg:{ src:80, sub:[
    ['1','Partner Master',10],['2','Recruitment & Onboarding',8],['3','Brand Relations',9],
    ['4','Alliances',6],['5','Referrals',8],['6','Deal Registration',7],
    ['7','Resellers',6],['8','Franchise',9],['9','Commercial Terms',8],['10','Performance',9] ] } },

/* ============ A05 · CIRCULAR & ASSET-BASED ========================== */

/* ---------------- M13 RENTAL & EQUIPMENT-AS-A-SERVICE --------------------- */
window.FX_MODULES.M13 = { area:'A05', en:'Rental & EaaS', bn:'ভাড়া ও ইকুইপমেন্ট', icon:'🎥', rail:'circular',
  desc:'8 asset categories — fleet register, availability, agreements & deposits, damage recovery, utilisation.',
  kpis:[ {l:'Utilisation (time)',v:'68.4%',d:'+4pt',up:1,st:'ok',spark:[52,56,59,62,64,66,68.4]},
          {l:'Fleet Units',v:'1,246',st:'info'},
          {l:'Late Returns',v:'22',st:'warn'},
          {l:'Damage Recovery',v:'৳ 84 K MTD',st:'info'},
          {l:'Turnaround',v:'1.6 d',d:'−0.2',up:1,st:'ok'},
          {l:'Deposits Held',v:'৳ 42.6 L',st:'info'} ],
  groups:[
    {en:'Fleet', screens:[
      {id:'M13-fleet', en:'Fleet Register', bn:'ফ্লিট রেজিস্টার', t:'g'},
      {id:'M13-availability', en:'Real-Time Availability', bn:'প্রাপ্যতা', t:'d'},
      {id:'M13-kits', en:'Kits & Accessories', bn:'কিট', t:'g'} ]},
    {en:'Booking', screens:[
      {id:'M13-reservations', en:'Reservations', bn:'সংরক্ষণ', t:'g'},
      {id:'M13-agreements', en:'Rental Agreements', bn:'ভাড়া চুক্তি', t:'f'},
      {id:'M13-deposits', en:'Security Deposits', bn:'নিরাপত্তা জামানত', t:'g'} ]},
    {en:'Lifecycle', screens:[
      {id:'M13-condition', en:'Condition Reports', bn:'অবস্থা রিপোর্ট', t:'g'},
      {id:'M13-damage', en:'Damage & Recovery', bn:'ক্ষতি ও পুনরুদ্ধার', t:'g'},
      {id:'M13-turnaround', en:'Turnaround & Re-Grade', bn:'টার্নঅ্যারাউন্ড', t:'g'} ]},
    {en:'Analytics', screens:[
      {id:'M13-utilisation', en:'Utilisation Analytics', bn:'ব্যবহার বিশ্লেষণ', t:'r'},
      {id:'M13-retire', en:'Fleet Health & Retirement', bn:'ফ্লিট স্বাস্থ্য', t:'r'} ]} ],
  reports:['Utilisation by Category','Damage & Loss Rate','Rental P&L','Late Return Analysis','Deposit Reconciliation'],
  forms:['Reservation','Rental Agreement (e-sign)','Condition Report','Damage Assessment'],
  cross:['M17 rental assets','M08 master agreements','M03 logistics','M15 rental pool stock'],
  freg:{ src:78, sub:[
    ['1','Fleet Register',9],['2','Availability & Reservation',12],['3','Agreements',10],
    ['4','Deposits & Waivers',8],['5','Condition & Damage',10],['6','Returns & Recovery',8],
    ['7','In-Rental Support',7],['8','Turnaround & PM',7],['9','Analytics',7] ] } },

/* ---------------- M14 TRADE-IN & REFURBISHMENT ---------------------------- */
window.FX_MODULES.M14 = { area:'A05', en:'Trade-In & Refurbishment', bn:'ট্রেড-ইন ও রিফার্বিশ', icon:'♻️', rail:'circular',
  desc:'Automated valuation, provenance screening, refurb work orders, A-D grading, harvest-to-parts, resale.',
  kpis:[ {l:'Trade-Ins MTD',v:'482',d:'+12%',up:1,spark:[340,368,392,416,440,462,482]},
          {l:'Refurb Yield',v:'88.2%',st:'ok',spark:[76,79,81,83,85,87,88.2]},
          {l:'Resale GMV MTD',v:'৳ 32.4 L',d:'+18%',up:1},
          {l:'Avg Margin (Refurb)',v:'31.6%',st:'ok'},
          {l:'Harvested Parts',v:'1,846',st:'info'},
          {l:'Ageing > 60d',v:'58 units',st:'warn'} ],
  groups:[
    {en:'Trade-In', screens:[
      {id:'M14-intake', en:'Trade-In Intake', bn:'ট্রেড-ইন গ্রহণ', t:'g'},
      {id:'M14-valuation', en:'Automated Valuation', bn:'স্বয়ংক্রিয় মূল্যায়ন', t:'c'},
      {id:'M14-provenance', en:'Provenance & IMEI Screen', bn:'উৎস যাচাই', t:'g'},
      {id:'M14-settlement', en:'Settlement', bn:'নিষ্পত্তি', t:'g'} ]},
    {en:'Refurbishment', screens:[
      {id:'M14-orders', en:'Refurb Work Orders', bn:'রিফার্ব অর্ডার', t:'g'},
      {id:'M14-qa', en:'QA & Battery Health', bn:'কিউএ', t:'g'},
      {id:'M14-grading', en:'A–D Grading', bn:'গ্রেডিং', t:'c'},
      {id:'M14-harvest', en:'Harvest to Parts', bn:'পার্টস সংগ্রহ', t:'g'} ]},
    {en:'Resale', screens:[
      {id:'M14-stock', en:'Graded Stock', bn:'গ্রেডেড স্টক', t:'g'},
      {id:'M14-listings', en:'Resale Listings', bn:'পুনঃবিক্রয়', t:'g'},
      {id:'M14-wty', en:'Refurb Warranty', bn:'রিফার্ব ওয়ারেন্টি', t:'g'},
      {id:'M14-economics', en:'Unit Economics', bn:'একক অর্থনীতি', t:'r'} ]} ],
  reports:['Trade-In Margin by Model','Refurb Cost per Grade','Ageing & Markdown','Resale Channel Performance','Harvest Yield'],
  forms:['Trade-In Request','Valuation Offer','Refurb Work Order','Grading Result'],
  cross:['M06 destruction gate','M31 refurb repairs','M15 graded stock','M38 online resale','M18 recycle routing'],
  freg:{ src:84, sub:[
    ['1','Intake (5 channels)',9],['2','Valuation Engine',9],['3','Provenance Screening',7],
    ['4','Settlement',8],['5','Bulk Buy-Back',6],['6','Destruction Gate',4],
    ['7','Refurbishment Orders',11],['8','Grading & QA',11],['9','Resale',10],['10','Harvesting',9] ] } },

/* ---------------- M18 E-WASTE & RECYCLING ---------------------------------- */
window.FX_MODULES.M18 = { area:'A05', en:'E-Waste & Recycling', bn:'ই-বর্জ্য ও রিসাইক্লিং', icon:'🌱', rail:'circular',
  desc:'Collection network, triage & disposition, certified partners, statutory DoE/BTRC returns, impact reporting.',
  kpis:[ {l:'Collected MTD (kg)',v:'4,214',d:'+9%',up:1,spark:[3120,3320,3520,3720,3920,4080,4214]},
          {l:'Diversion Rate',v:'92.4%',st:'ok',spark:[78,82,85,88,90,91,92.4]},
          {l:'Disposal Certificates',v:'100%',st:'ok'},
          {l:'Certified Partners',v:'6',st:'ok'},
          {l:'Battery Handlers',v:'compliant',st:'ok'},
          {l:'CO₂e Avoided MTD',v:'84.2 t',st:'info'} ],
  groups:[
    {en:'Collection', screens:[
      {id:'M18-collections', en:'Collections & Bookings', bn:'সংগ্রহ', t:'g'},
      {id:'M18-events', en:'Collection Events', bn:'সংগ্রহ ইভেন্ট', t:'g'} ]},
    {en:'Processing', screens:[
      {id:'M18-triage', en:'Triage & Disposition', bn:'ট্রায়াজ', t:'c'},
      {id:'M18-batches', en:'Batches by Material', bn:'ব্যাচ', t:'g'},
      {id:'M18-battery', en:'Lithium-Ion Handling', bn:'ব্যাটারি পরিচালনা', t:'g'} ]},
    {en:'Partners & Compliance', screens:[
      {id:'M18-partners', en:'Certified Partner Register', bn:'সনদপ্রাপ্ত পার্টনার', t:'g'},
      {id:'M18-certificates', en:'Disposal Certificates', bn:'নিষ্পত্তি সনদ', t:'g'},
      {id:'M18-returns', en:'DoE / BTRC Returns', bn:'সরকারি রিটার্ন', t:'g'} ]},
    {en:'Impact', screens:[
      {id:'M18-impact', en:'Carbon & Impact Estimation', bn:'কার্বন ও প্রভাব', t:'r'},
      {id:'M18-esg', en:'Sustainability Reporting', bn:'স্থায়িত্ব রিপোর্ট', t:'r'} ]} ],
  reports:['Collection Volume Trend','Disposition Mix','Material Recovery','Compliance Evidence Pack','Impact & Diversion Report'],
  forms:['Collection Booking','Triage Decision','Batch Transfer Note','Disposal Record'],
  cross:['M06 data-bearing destruction','M14 recycle routing','M42 partner qualification','M47 site storage'],
  freg:{ src:64, sub:[
    ['1','Collection Network',10],['2','Chain of Custody',8],['3','Triage & Disposition',9],
    ['4','Destruction Gate',4],['5','Certified Partners',7],['6','Batches & Transfers',8],
    ['7','Certificates',6],['8','Statutory Returns',5],['9','Impact Reporting',7] ] } },

/* ============ A06 · SUPPLY CHAIN & INVENTORY ========================= */

/* ---------------- M15 SPARE PARTS & INVENTORY ------------------------------ */
window.FX_MODULES.M15 = { area:'A06', en:'Spare Parts & Inventory', bn:'স্পেয়ার পার্টস ও ইনভেন্টরি', icon:'🧰', rail:'supply',
  desc:'Stock ledger across 6 ownership classes — serial/lot trace, van stock, valuation, transfers, counts.',
  kpis:[ {l:'Inventory Accuracy',v:'97.8%',d:'+2.6pt',up:1,st:'ok',spark:[92,93,94,95.5,96.5,97.2,97.8]},
          {l:'Stock Value',v:'৳ 8.62 Cr',st:'info',spark:[7.4,7.7,7.9,8.1,8.3,8.5,8.62]},
          {l:'Part Availability',v:'93.6%',st:'ok',spark:[84,86,88,90,91.5,92.6,93.6]},
          {l:'Dead Stock',v:'3.8%',st:'ok'},
          {l:'Van Variance',v:'0.6%',st:'ok'},
          {l:'Turns (annualised)',v:'6.4',st:'ok'} ],
  groups:[
    {en:'Stock Ledger', screens:[
      {id:'M15-onhand', en:'On-Hand by Location', bn:'স্টক লেজার', t:'g'},
      {id:'M15-ownership', en:'6 Ownership Classes', bn:'মালিকানা শ্রেণি', t:'g'},
      {id:'M15-movements', en:'Issues & Returns', bn:'ইস্যু ও ফেরত', t:'g'},
      {id:'M15-network', en:'Network Availability Search', bn:'নেটওয়ার্ক অনুসন্ধান', t:'c'} ]},
    {en:'Traceability', screens:[
      {id:'M15-serials', en:'Serial & Lot Trace', bn:'সিরিয়াল ট্রেস', t:'g'},
      {id:'M15-genealogy', en:'Consumption Genealogy', bn:'ব্যবহার বংশতালিকা', t:'r'} ]},
    {en:'Van Stock', screens:[
      {id:'M15-van', en:'Van Stock by Technician', bn:'ভ্যান স্টক', t:'g'},
      {id:'M15-replen', en:'Replenishment & Par', bn:'পূরণকরণ', t:'g'},
      {id:'M15-recon', en:'Daily Reconciliation', bn:'দৈনিক মিলকরণ', t:'c'} ]},
    {en:'Control', screens:[
      {id:'M15-counts', en:'Cycle & Full Counts', bn:'গণনা', t:'c'},
      {id:'M15-transfers', en:'Inter-Branch Transfers', bn:'শাখা স্থানান্তর', t:'g'},
      {id:'M15-quarantine', en:'Quarantine & Scrap', bn:'কোয়ারেন্টাইন', t:'g'},
      {id:'M15-rtv', en:'RTV Initiation', bn:'ফেরত প্রেরণ', t:'g'} ]},
    {en:'Valuation & Analysis', screens:[
      {id:'M15-valuation', en:'Valuation (FIFO/WAC)', bn:'মূল্যায়ন', t:'r'},
      {id:'M15-ageing', en:'Ageing & Obsolescence', bn:'বয়স ও অবচয়', t:'r'},
      {id:'M15-abc', en:'ABC / XYZ / Criticality', bn:'এবিসি বিশ্লেষণ', t:'r'} ]} ],
  reports:['Stock Valuation by Class','Inventory Accuracy Audit','Ageing & Dead Stock','Van Stock Variance','Transfer Performance','ABC Segmentation'],
  forms:['Goods Receipt (inspection gate)','Stock Issue','Transfer Request','Cycle Count','Scrap Order'],
  cross:['M41 warehouse execution','M16 procurement','M02 van consumption','M09 consignment stock','M31 bench stock'],
  freg:{ src:107, sub:[
    ['1','On-Hand & Classes',12],['2','Location Hierarchy',8],['3','Ownership Segregation',9],
    ['4','Reservations',7],['5','Issue / Return / Consumption',10],['6','Van Stock',11],
    ['7','Serial & Lot Trace',10],['8','Valuation',8],['9','Goods Receipt',7],
    ['10','Counting',9],['11','Ageing & Analysis',8],['12','Transfers & RTV',8] ] } },

/* ---------------- M41 WAREHOUSE MANAGEMENT ---------------------------------- */
window.FX_MODULES.M41 = { area:'A06', en:'Warehouse Management', bn:'ওয়্যারহাউস ব্যবস্থাপনা', icon:'🏭', rail:'supply',
  desc:'Physical execution — bins & slots, directed put-away, wave picking, packing, RF mobile, task interleaving.',
  kpis:[ {l:'Pick Accuracy',v:'99.7%',st:'ok',spark:[98.4,98.7,98.9,99.2,99.4,99.6,99.7]},
          {l:'Lines Picked Today',v:'6,842',st:'info'},
          {l:'Waves Open',v:'8',st:'info'},
          {l:'Dock Appointments',v:'14',st:'info'},
          {l:'Labour Efficiency',v:'112%',st:'ok'},
          {l:'Short-Picks',v:'6',st:'warn'} ],
  groups:[
    {en:'Structure', screens:[
      {id:'M41-zones', en:'Zones, Aisles & Bins', bn:'জোন ও বিন', t:'g'},
      {id:'M41-slotting', en:'Slotting & Re-Slotting', bn:'স্লটিং', t:'g'} ]},
    {en:'Inbound', screens:[
      {id:'M41-docks', en:'Dock Appointments', bn:'ডক অ্যাপয়েন্টমেন্ট', t:'g'},
      {id:'M41-receiving', en:'Scan Receiving', bn:'রিসিভিং', t:'c'},
      {id:'M41-putaway', en:'Directed Put-Away', bn:'পুট-অ্যাওয়ে', t:'g'} ]},
    {en:'Outbound', screens:[
      {id:'M41-waves', en:'Wave Planning', bn:'ওয়েভ পরিকল্পনা', t:'c'},
      {id:'M41-picking', en:'Pick Strategies', bn:'পিকিং', t:'g'},
      {id:'M41-packing', en:'Packing & Cartons', bn:'প্যাকিং', t:'g'},
      {id:'M41-staging', en:'Staging & Load', bn:'স্টেজিং', t:'g'} ]},
    {en:'Floor Ops', screens:[
      {id:'M41-rf', en:'RF Mobile App', bn:'আরএফ অ্যাপ', t:'d'},
      {id:'M41-tasks', en:'Task Management', bn:'কাজ ব্যবস্থাপনা', t:'g'},
      {id:'M41-counting', en:'Floor Counts', bn:'ফ্লোর গণনা', t:'g'} ]} ],
  reports:['Throughput by Shift','Pick Accuracy Trend','Wave Cycle Time','Labour Productivity','Bin Utilisation Heatmap'],
  forms:['Bin','Wave Template','Dock Appointment','Packing Station Config'],
  cross:['M15 stock ledger','M16 goods receipt','M03 outbound staging','M44 import receiving'],
  freg:{ src:78, sub:[
    ['1','Physical Structure',8],['2','Slotting',7],['3','Inbound & Put-Away',12],
    ['4','Wave Planning',9],['5','Picking',11],['6','Packing & Staging',8],
    ['7','Replenishment',6],['8','RF Execution',8],['9','Labour & Analytics',9] ] } },

/* ---------------- M16 PROCUREMENT -------------------------------------------- */
window.FX_MODULES.M16 = { area:'A06', en:'Procurement & Sourcing', bn:'ক্রয় ও সোর্সিং', icon:'🛍️', rail:'supply',
  desc:'Demand-to-PO, RFQ with normalised comparison, three-way match, blanket orders, expediting, spend analysis.',
  kpis:[ {l:'Open PRs',v:'42',st:'info',spark:[36,38,39,40,41,42,42]},
          {l:'POs Awaiting Approval',v:'11',st:'warn'},
          {l:'3-Way Match Exceptions',v:'3.2%',st:'ok',spark:[7.4,6.6,5.8,5.0,4.2,3.6,3.2]},
          {l:'Vendor OTD',v:'93.8%',st:'ok',spark:[86,88,89.5,91,92.2,93,93.8]},
          {l:'Spend Under Contract',v:'86.4%',st:'ok'},
          {l:'Emergency Purchases',v:'4',st:'warn'} ],
  groups:[
    {en:'Requisitions', screens:[
      {id:'M16-prs', en:'Purchase Requisitions', bn:'ক্রয় অনুরোধ', t:'g'},
      {id:'M16-consol', en:'Cross-Branch Consolidation', bn:'একত্রীকরণ', t:'c'} ]},
    {en:'Sourcing', screens:[
      {id:'M16-rfqs', en:'RFQ Events', bn:'আরএফকিউ', t:'g'},
      {id:'M16-compare', en:'Bid Comparison', bn:'দর তুলনা', t:'f'},
      {id:'M16-award', en:'Award Decisions', bn:'পুরস্কার সিদ্ধান্ত', t:'g'} ]},
    {en:'Orders', screens:[
      {id:'M16-pos', en:'Purchase Orders', bn:'ক্রয় আদেশ', t:'g'},
      {id:'M16-blanket', en:'Blanket / Call-Off', bn:'ব্ল্যাঙ্কেট আদেশ', t:'g'},
      {id:'M16-expedite', en:'Expediting Desk', bn:'ত্বরান্বিতকরণ', t:'c'} ]},
    {en:'Receiving & Match', screens:[
      {id:'M16-grn', en:'Goods Receipts', bn:'পণ্য গ্রহণ', t:'g'},
      {id:'M16-inspection', en:'Inspection Outcomes', bn:'পরিদর্শন', t:'g'},
      {id:'M16-match', en:'3-Way Match Workbench', bn:'ত্রিমুখী মিলকরণ', t:'c'} ]},
    {en:'Analysis', screens:[
      {id:'M16-spend', en:'Spend Analysis', bn:'ব্যয় বিশ্লেষণ', t:'r'},
      {id:'M16-pricehist', en:'Price History & Alerts', bn:'মূল্য ইতিহাস', t:'g'},
      {id:'M16-rtv', en:'RTV Lifecycle', bn:'ফেরত জীবনচক্র', t:'g'} ]} ],
  reports:['Spend by Category & Vendor','Match Exception Pareto','OTD by Vendor','Price Variance Alert','Maverick Spend','PO Cycle Time'],
  forms:['Purchase Requisition','RFQ','Purchase Order','GRN','RTV Request'],
  cross:['M43 planned orders','M42 supplier gate','M52 invoices','M44 imports','P05 vendor portal'],
  freg:{ src:88, sub:[
    ['1','Demand Intake',8],['2','Requisition & Approval',10],['3','Consolidation',6],
    ['4','RFQ & Bidding',12],['5','PO Lifecycle',11],['6','Blanket Orders',6],
    ['7','Expediting',7],['8','GRN & Inspection',9],['9','3-Way Match',10],['10','Spend Analysis',9] ] } },

/* ---------------- M42 SUPPLIER RELATIONSHIP ---------------------------------- */
window.FX_MODULES.M42 = { area:'A06', en:'Supplier Relationship', bn:'সরবরাহকারী সম্পর্ক', icon:'🧑‍💼', rail:'supply',
  desc:'Supplier qualification gate, scorecards, corrective actions, risk assessment, compliance screening.',
  kpis:[ {l:'Qualified Suppliers',v:'186',st:'info'},
          {l:'Scorecard Avg',v:'87.4',st:'ok'},
          {l:'CARs Open',v:'9',st:'warn'},
          {l:'Docs Expiring (60d)',v:'14',st:'warn'},
          {l:'Single-Source Items',v:'62',st:'warn'},
          {l:'Restricted Suppliers',v:'3',st:'err'} ],
  groups:[
    {en:'Register', screens:[
      {id:'M42-suppliers', en:'Supplier Directory', bn:'সরবরাহকারী তালিকা', t:'g'},
      {id:'M42-segments', en:'Segmentation', bn:'সেগমেন্টেশন', t:'g'},
      {id:'M42-docs', en:'Document Register', bn:'দলিল রেজিস্টার', t:'g'} ]},
    {en:'Qualification', screens:[
      {id:'M42-qualification', en:'Qualification Workflow', bn:'যোগ্যতা যাচাই', t:'c'},
      {id:'M42-gate', en:'Activation Gate (M16)', bn:'অ্যাক্টিভেশন গেট', t:'g'},
      {id:'M42-requal', en:'Re-Qualification', bn:'পুনঃযোগ্যতা', t:'g'} ]},
    {en:'Performance', screens:[
      {id:'M42-scorecards', en:'Scorecards', bn:'স্কোরকার্ড', t:'g'},
      {id:'M42-cars', en:'Corrective Actions', bn:'সংশোধনী কর্ম', t:'g'},
      {id:'M42-reviews', en:'Review Cycles', bn:'পর্যালোচনা', t:'c'} ]},
    {en:'Risk & Compliance', screens:[
      {id:'M42-risk', en:'Risk Assessment', bn:'ঝুঁকি মূল্যায়ন', t:'r'},
      {id:'M42-screening', en:'Sanctions / COI / ABAC', bn:'স্ক্রিনিং', t:'g'} ]} ],
  reports:['Supplier Scorecard League','CAR Closure Performance','Risk Heat Map','Contract Coverage','Compliance Screening Log'],
  forms:['Supplier Profile','Qualification Questionnaire','CAR','Risk Assessment'],
  cross:['M33 party extension','M16 activation gate','P05 vendor portal','M40 brand class'],
  freg:{ src:71, sub:[
    ['1','Supplier Profiles',9],['2','Segmentation',6],['3','Qualification',10],
    ['4','Documents & Validity',8],['5','Contracts & Price Lists',7],['6','Scorecards',9],
    ['7','Corrective Actions',7],['8','Risk Assessment',9],['9','Compliance Screening',6] ] } },

/* ---------------- M43 DEMAND PLANNING ----------------------------------------- */
window.FX_MODULES.M43 = { area:'A06', en:'Demand Planning', bn:'চাহিদা পরিকল্পনা', icon:'📈', rail:'supply',
  desc:'Forecast orchestration with MAPE tracking, safety stock, reorder policies, multi-echelon rebalancing.',
  kpis:[ {l:'Forecast MAPE',v:'18.4%',d:'−2.2pt',up:1,st:'ok',spark:[26,24.6,23.2,21.8,20.4,19.2,18.4]},
          {l:'Service Level Target',v:'96%',st:'ok'},
          {l:'Planned Orders',v:'64',st:'info'},
          {l:'Stockout Incidents',v:'11',d:'−6',up:1,st:'warn'},
          {l:'Excess Stock Value',v:'৳ 64 L',d:'−৳ 8 L',up:1,st:'warn'},
          {l:'Rebalance Proposals',v:'7',st:'info'} ],
  groups:[
    {en:'Forecasting', screens:[
      {id:'M43-history', en:'History Assembly', bn:'ইতিহাস সংকলন', t:'g'},
      {id:'M43-models', en:'Model Orchestration', bn:'মডেল অর্কেস্ট্রেশন', t:'c'},
      {id:'M43-accuracy', en:'Accuracy & Bias (MAPE)', bn:'নির্ভুলতা', t:'r'} ]},
    {en:'Policies', screens:[
      {id:'M43-segments', en:'Part Segmentation', bn:'পার্টস সেগমেন্টেশন', t:'g'},
      {id:'M43-safety', en:'Safety Stock & ROP', bn:'সেফটি স্টক', t:'g'},
      {id:'M43-leadtime', en:'Lead-Time Modelling', bn:'লিড-টাইম', t:'g'} ]},
    {en:'Execution', screens:[
      {id:'M43-planned', en:'Planned Orders → PR', bn:'পরিকল্পিত অর্ডার', t:'g'},
      {id:'M43-rebalance', en:'Network Rebalancing', bn:'নেটওয়ার্ক পুনঃসমন্বয়', t:'c'},
      {id:'M43-vanpar', en:'Van-Stock Par Calculation', bn:'ভ্যান প্যারামিটার', t:'g'} ]},
    {en:'Simulation', screens:[
      {id:'M43-whatif', en:'What-If Simulation', bn:'সিমুলেশন', t:'c'} ]} ],
  reports:['Forecast Accuracy by Class','Stockout Root Causes','Excess & Obsolescence Exposure','Rebalancing Savings','New-Part Introduction'],
  forms:['Review Cycle','Policy Assignment','Rebalance Proposal'],
  cross:['M26 forecast models','M16 planned orders','M15 stock positions','M37 lifecycle states'],
  freg:{ src:58, sub:[
    ['1','History & Cleansing',7],['2','Segmentation',6],['3','Forecast Orchestration',8],
    ['4','Accuracy Tracking',6],['5','Safety Stock & ROP',9],['6','Lead-Time',5],
    ['7','Planned Orders',6],['8','Multi-Echelon Rebalancing',7],['9','What-If',4] ] } },

/* ---------------- M44 IMPORT & TRADE COMPLIANCE ------------------------------- */
window.FX_MODULES.M44 = { area:'A06', en:'Import & Trade Compliance', bn:'আমদানি ও বাণিজ্য', icon:'🚢', rail:'supply',
  desc:'LC/TT lifecycle, HS classification, ASYCUDA Bill of Entry, duty cascade, landed-cost allocation.',
  kpis:[ {l:'Active Imports',v:'8',st:'info'},
          {l:'LCs Open',v:'3',st:'info'},
          {l:'Duty Accuracy',v:'±1.4%',st:'ok'},
          {l:'Demurrage Incidents',v:'0',st:'ok'},
          {l:'Landed-Cost Variance',v:'1.8%',st:'ok'},
          {l:'Cycle Time (order→release)',v:'21 d',d:'−3 d',up:1,st:'ok'} ],
  groups:[
    {en:'Orders & Finance', screens:[
      {id:'M44-orders', en:'Import Orders', bn:'আমদানি অর্ডার', t:'g'},
      {id:'M44-proforma', en:'Proforma Invoices', bn:'প্রোফর্মা', t:'g'},
      {id:'M44-lc', en:'Letters of Credit', bn:'এলসি', t:'g'},
      {id:'M44-incoterms', en:'Incoterms & FX', bn:'ইনকোটার্ম', t:'g'} ]},
    {en:'Compliance', screens:[
      {id:'M44-hs', en:'HS Classification', bn:'এইচএস কোড', t:'g'},
      {id:'M44-irc', en:'IRC & Restrictions', bn:'আইআরসি', t:'g'},
      {id:'M44-lca', en:'LCA via Dealer Bank', bn:'এলসিএ', t:'g'} ]},
    {en:'Shipping & Customs', screens:[
      {id:'M44-docs', en:'Shipping Documents', bn:'শিপিং দলিল', t:'g'},
      {id:'M44-arrival', en:'Arrival & Port Handling', bn:'বন্দর পরিচালনা', t:'g'},
      {id:'M44-boe', en:'Bill of Entry (ASYCUDA)', bn:'বিল অব এন্ট্রি', t:'f'},
      {id:'M44-duty', en:'Duty Cascade (CD/RD/SD/VAT/AT/AIT)', bn:'শুল্ক', t:'r'} ]},
    {en:'Costing', screens:[
      {id:'M44-landed', en:'Landed Cost Allocation', bn:'ল্যান্ডেড কস্ট', t:'c'},
      {id:'M44-cf', en:'C&F Management', bn:'সিঅ্যান্ডএফ', t:'g'} ]} ],
  reports:['Landed Cost by Shipment','Duty & Tax Cascade','Cycle-Time Analysis','Demurrage Avoidance','FX Exposure'],
  forms:['Import Order','LC Application','HS Ruling Request','Bill of Entry'],
  cross:['M16 import POs','M50 trade finance','M51 import VAT/duty','M15 landed cost'],
  freg:{ src:64, sub:[
    ['1','Import Order Lifecycle',9],['2','LC & Payments',10],['3','HS Classification',7],
    ['4','Eligibility & IRC',5],['5','Shipping & Insurance',8],['6','Port & Customs',9],
    ['7','Duty Computation',8],['8','Landed Cost',8] ] } }
;
})();
