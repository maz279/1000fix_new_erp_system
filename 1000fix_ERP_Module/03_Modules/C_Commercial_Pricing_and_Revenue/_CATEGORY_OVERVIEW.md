---
id: FIX-ERP2-CAT-C
category: C
category_name: Commercial, Pricing & Revenue
module_count: 9
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT
---

# Category C — Commercial, Pricing & Revenue

**9 modules · Category owner: Chief Commercial Officer**

---

## 1. What Belongs in This Category

What the Company sells, what it charges, what it agrees to, and every route to market.

If a capability answers *"what is the offer, what is the price, what did we commit to, and
through which channel"*, it belongs here. If it answers *"did the money arrive"*, it belongs
to Category G.

---

## 2. Modules

| ID | Module | Status | Priority | Wave | One-Line Definition |
|---|---|---|:--:|:--:|---|
| **M37** | Product & Service Catalogue Management ★ | New | P0 | W1 | The definition of everything sellable: services, kits, parts, plans, rental SKUs, refurbished grades, subscriptions — with repair bills of material |
| **M11** | Pricing, Rate Cards & Dynamic Pricing | Re-scoped | P1 | W3 / W7 | Every price in the business: rate cards, price books, customer-specific pricing, discount governance, dynamic pricing |
| **M36** | Quotation, Estimation & Tender Management ★ | New | P1 | W3 | Estimates, quotations, competitive bidding, corporate tenders and customer approval loops |
| **M08** | Contract Lifecycle Management | Re-scoped | P1 | W4 | Every agreement across 14 contract product families: scope, entitlement, SLA, amendment, renewal, profitability |
| **M09** | Warranty, Protection Plans & Claims | Retained | P0 | W4 | Warranty entitlement, seven protection-product families, and recovery of money from 17+ brand partners |
| **M39** | Subscription & Recurring Revenue ★ | New | P1 | W4 | Recurring and usage-based billing mechanics, proration, MRR/ARR, plan changes and churn |
| **M38** | E-Commerce & Digital Storefront ★ | New | P1 | W7 | Selling 1000FiX's own products and services online: catalogue browsing, cart, checkout, fulfilment, returns |
| **M12** | Marketplace & Seller Ecosystem | Re-scoped | P1 | W7 | The aggregator: third-party sellers, listings, job broadcast, ratings, disputes, commission and payouts |
| **M40** | Partner, Channel, Alliance & Franchise ★ | New | P2 | W7 | Relationship management for brand partners, alliance partners, referral partners, resellers and franchise branches |

★ = new in v2.1 after enterprise benchmarking.

---

## 3. The Commercial Chain

These nine modules form one chain. Each link has exactly one owner.

```
   M37 CATALOGUE          "What can we sell?"
        │                  Service definitions, kits, repair BOM, SKUs, plan definitions
        ▼
   M11 PRICING            "What does it cost the customer?"
        │                  Rate cards, price books, customer pricing, dynamic rules
        ▼
   M36 QUOTATION          "What did we offer this specific customer?"
        │                  Estimate build-up, versions, approval, bidding, tenders
        ▼
   ┌────┴────┬──────────┬──────────┬──────────┐
   ▼         ▼          ▼          ▼          ▼
 M08       M09        M39       M38        M12
CONTRACT  WARRANTY  SUBSCRIPTION E-COMM  MARKETPLACE
"What did  "What is  "What      "Direct   "Third-party
we commit  covered?" recurs?"   sale"     sale"
 to?"
   │         │          │          │          │
   └─────────┴──────────┴──────────┴──────────┘
                        │
                        ▼
              M53 REVENUE & SETTLEMENT  (Category G)
              M20 ACCOUNTS RECEIVABLE   (Category G)
```

---

## 4. Three Boundaries That Must Not Blur

### 4.1 Catalogue (M37) vs Pricing (M11)

| | M37 Catalogue | M11 Pricing |
|---|---|---|
| Owns | *What* the item is: definition, attributes, components, applicability, standard time | *What it costs*: rate, currency, validity, customer applicability, rule |
| Analogue | SAP *Product Master* / *Service Product* · Oracle *Product Hub* | SAP *Condition Technique* · Oracle *Pricing Cloud* |
| Changes when | The service offering changes | Commercial strategy changes |

**Rule:** a price never lives on a catalogue item. A catalogue item never carries a discount.

### 4.2 Contract (M08) vs Subscription (M39)

| | M08 Contract | M39 Subscription |
|---|---|---|
| Owns | The **agreement**: parties, scope, covered assets, entitlements, SLA, terms, amendments, renewal | The **billing mechanics**: schedule, cycle, proration, usage rating, MRR/ARR, plan change, dunning trigger |
| Analogue | SAP *Service Contract* · IFS *Contract Management* | Oracle *Subscription Management* · Zuora-class billing |
| Question it answers | "What did we promise?" | "What do we bill, when, and how much?" |

**Rule:** M08 defines entitlement; M39 turns it into money owed. A contract with no recurring
charge has no M39 record. A subscription always has an M08 contract behind it.

### 4.3 E-Commerce (M38) vs Marketplace (M12)

| | M38 E-Commerce | M12 Marketplace |
|---|---|---|
| Seller | 1000FiX | Third-party engineer or shop |
| Inventory | Owned (M15) | Seller-declared |
| Revenue | Full sale value | Commission and fees |
| Liability | 1000FiX | Shared, per the seller agreement |
| VAT treatment | Principal | Principal or agent — a formal decision (see risk RSK-022) |
| Fulfilment | M03 logistics or M02 field | Seller, with 1000FiX escalation |

**Rule:** one storefront, two supply models. The customer sees one experience; the ledger
sees two revenue treatments.

---

## 5. Category Boundary Map

| Capability | Owned By | Not Owned By |
|---|---|---|
| Service, part and plan definitions | **M37** | M11, M15, M38 (all reference) |
| Repair bill of material and standard times | **M37** | M31 (consumes) |
| All prices and discount policy | **M11** | M36, M38, M12 (all request a price) |
| Estimate and quotation documents | **M36** | M01 (displays), M11 (prices) |
| Customer approval of an estimate | **M36** | M01 |
| Contract entitlement definition and consumption | **M08** | M39, M05 |
| Recurring invoice generation | **M39** | M20 (posts and collects) |
| Warranty entitlement validation | **M09** | M01 (calls it) |
| Brand claim submission and reimbursement | **M09** | M20 (receives the cash) |
| Seller onboarding, listings, ratings, disputes | **M12** | M40 |
| Brand partner, alliance and franchise relationships | **M40** | M12, M42 |
| Supplier commercial relationships | **M42** (Category E) | M40 |
| Commission calculation and payout execution | **M53** (Category G) | M12 (defines the scheme) |
| Loyalty offers applied at quotation | **M10** (Category B) | M11 (applies, does not define) |

---

## 6. The Fourteen Contract Product Families

M08 must model all of these without code changes. This is why it is a contract *engine*, not
an AMC table.

| Family | Products | Source |
|---|---|---|
| Residential AMC (RAMC) | 6 appliance packages | Business Plan |
| Commercial AMC | Office, retail, restaurant equipment | Business Plan |
| IT Infrastructure AMC | Servers, network, storage, backup | Business Plan |
| Healthcare Equipment AMC | With mandatory calibration | Business Plan |
| Specialty Equipment AMC | Manufacturing, R&D, telecom | Business Plan |
| Managed Services | Basic · Comprehensive · Security · Cloud · DR/BC · IT Strategy | Business Plan |
| Mobile & Appliance Service | Basic · Comprehensive · Extended Warranty · Accidental Damage · Priority | Business Plan |
| Rental master agreements | Framework with call-off | Business Plan |
| Marketplace seller agreements | Terms, commission, standards | Service App SOW |
| Brand partner agreements | Authorised service terms, rate cards | Company Profile |

---

## 7. The Seven Protection Product Families

M09 must sell and honour all of these.

Standard Warranty Extension · Accidental Damage Protection · Extended Repair Coverage ·
Mobile Device Protection · Home Appliance Protection · Computer & Laptop Care ·
Customised Coverage

---

## 8. Category KPIs

| KPI | Baseline | Target | Owning Module |
|---|---|---|---|
| Catalogue items with complete definition | unmeasured | 100% | M37 |
| Quotation-to-order conversion | unmeasured | > 78% | M36 |
| Average quotation turnaround | unmeasured | < 2 h | M36 |
| Gross margin on paid repair | baseline | +4 pts | M11 |
| Price override exceptions | unmeasured | < 5% | M11 |
| Dynamic pricing margin uplift | 0 | +3–6% | M11 |
| AMC / RAMC renewal rate | 60% | 88% | M08 |
| Contract base growth | baseline | 2.5× | M08 |
| Contracts with negative margin | unknown | < 3% | M08 |
| Claims submitted within 72 h | ~50% at 30–90 d | > 95% | M09 |
| Warranty revenue leakage | 15–20% | < 2% | M09 |
| Warranty product attach rate | unmeasured | > 18% | M09 |
| Subscription billing accuracy | n/a | > 99.5% | M39 |
| Approved active marketplace sellers | 0 | 500 | M12 |
| Marketplace share of job volume | 0% | > 25% | M12 |
| Marketplace dispute rate | n/a | < 1.5% | M12 |
| Active referral / alliance partners | 0 | > 200 | M40 |

---

## 9. Category Delivery Sequence

```
W1   M37 Catalogue ──────────────► nothing can be sold without it
W3   M11 Pricing ────┐
     M36 Quotation ──┴───────────► estimates and approvals
W4   M08 Contract ───┐
     M09 Warranty ───┤
     M39 Subscription┴───────────► agreements and recurring revenue
W7   M38 E-Commerce ─┐
     M12 Marketplace ┤
     M40 Partner ────┴───────────► all routes to market live
```

---

## 10. Category Risks

| Risk | Impact | Mitigation | Owning Module |
|---|---|---|---|
| Marketplace VAT and liability model wrong | **Critical** — restatement or regulatory action | External tax and legal opinion three months before build; principal-vs-agent decision documented | M12 |
| Marketplace quality failure damages the brand | **Critical** | Same QC and evidence standards as owned work; automatic consequences on score | M12 |
| Prices maintained in more than one place | High — margin leakage and customer disputes | M11 is the only source of price; every other module requests it | M11 |
| Contract engine cannot model a new product family | High — a business line is blocked | Template-driven engine validated against all 14 families before Wave 4 gate | M08 |
| Dynamic pricing changes a price after acceptance | High — trust damage | Hard rule: price is fixed at acceptance; changes require re-approval | M11 |
| Estimates and quotations diverge from the invoice | High — disputes | One quotation object flows to one invoice; variance requires a documented reason | M36 / M20 |

---

*Category C · 1000FiX ERP System v2.0*
