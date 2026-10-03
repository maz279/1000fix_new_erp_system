---
id: FIX-ERP2-M38
module_id: M38
module_code: ECM
module_name: E-Commerce & Digital Storefront
category: C — Commercial, Pricing & Revenue
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Commercial Officer
system_owner: Digital Squad
priority: P1
wave: W7
---

# M38 — E-Commerce & Digital Storefront
### Category C · Code `ECM` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M38 |
| **Module code** | `ECM` |
| **Category** | C — Commercial, Pricing & Revenue |
| **Status** | ★ New — split out of the former M12 "E-Commerce, Parts Retail & Marketplace" during v2.1 re-scoping |
| **Priority** | **P1** |
| **Delivery wave** | W7 (Months 27–30) |
| **Business owner** | Chief Commercial Officer |
| **System owner** | Digital Squad |
| **Delivery layers** | L1 (Odoo `website_sale`) + L2 (OCA `website_sale_*`, `sale_order_type`) + L4/L5 (headless commerce API + Next.js storefront) |
| **Custom modules** | `cd_commerce_api`, `cd_cart_checkout`, `cd_service_booking_commerce`, `cd_returns_rma`, `cd_merchandising` |
| **Requirement range** | FR-ECM-001 … FR-ECM-056 |
| **Requirement count** | **56** *(measured; register estimate 40)* |
| **Effort estimate** | **30 person-weeks** *(measured; register estimate 24 PW)* |
| **Depends on** | M37 Catalogue · M11 Pricing · M15 Inventory · M33 Party Master · M20 Receivable · M51 Tax · M03 Logistics · M09 Warranty · M10 Loyalty · M28 Integration · M29 Identity |
| **Depended on by** | M01, M03, M12, M14, M13, M15, M20, M53, M35, M25, M26 · Portals **P01**, **P04** |

---

## 2. Purpose

M38 is **1000FiX selling its own things online**: spare parts, accessories, refurbished devices,
protection plans, AMC packages, rental bookings and service appointments — through one
storefront, one cart and one checkout, on the web and in the mobile app.

The distinction that defines this module is the one the category overview draws in §4.3: on M38,
**the seller is 1000FiX**. The inventory is owned, the revenue is the full sale value, the
liability is ours, and the VAT treatment is that of a principal. When the seller is a third
party, the transaction belongs to M12 Marketplace. The customer sees one storefront; the ledger
sees two revenue treatments.

M38 is also, uniquely in Category C, a module whose success is measured in conversion. Every
other commercial module is judged on accuracy and control. This one is judged on whether a
customer in Chattogram, on a mid-range Android phone and a 3G connection, can find a laptop
charger and buy it in under two minutes.

### Why It Exists

1000FiX has parts, accessories and refurbished stock in 51+ locations and no way to sell any of
it beyond the counter. The business plan commits to refurbished device resale, spare parts and
accessory retail, and rental booking — three revenue streams with no digital channel. The
Integrated Portal roadmap and the Service App SOW both assume a storefront that does not exist.

Meanwhile the customer portal (P01) already needs a commerce surface for protection plans,
contract renewal, and paying for repairs. Building that piecemeal inside each module would
produce four incompatible checkouts. M38 exists so there is one.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.12 (BR-ECM-*) | Online catalogue, cart, checkout, order tracking, returns |
| ERP URD §10 (US-ECM-*) | Customer purchase and return stories |
| Business Plan §Refurbished Device Resale | Refurbished units sold online, graded, with warranty |
| Business Plan §Spare Parts & Accessories | Parts and accessory retail as revenue stream 5 |
| Business Plan §Rental | Online rental booking |
| `04-00` P01 §Shop | "Browse and buy parts, accessories and refurbished devices · rental booking · cart, checkout and order tracking · returns" |
| `04-00` P04 §Procurement | Corporate ordering against agreed pricing |
| Service App SOW §Product Purchase | In-app purchase of parts and accessories |
| `_CATEGORY_OVERVIEW.md` §4.3 | The E-Commerce vs Marketplace boundary and the principal VAT position |
| Executive Summary §3 | Revenue streams 5, 10, 11 and 14 depend on a digital sales channel |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The storefront domain: catalogue browsing, search, faceted navigation, product detail |
| 2 | Merchandising: collections, featured sets, cross-sell, up-sell, recently viewed, recommendations |
| 3 | Device-compatibility filtering ("parts that fit my model") |
| 4 | Cart: persistent, cross-device, multi-line, mixed-type (goods + services + plans) |
| 5 | Checkout: address, delivery mode, slot selection, payment, order confirmation |
| 6 | Guest checkout and account-linked checkout |
| 7 | **Service booking commerce** — booking a repair, a rental or a data-service appointment as a purchasable item |
| 8 | Protection plan and AMC/RAMC purchase and renewal online |
| 9 | Refurbished device sales with grade disclosure, unit-level identity and warranty terms |
| 10 | Rental booking: availability, hire period, deposit, terms acceptance |
| 11 | Delivery options: home delivery, branch pickup, scheduled slot, express |
| 12 | Payment orchestration: bKash, Nagad, card, bank transfer, cash on delivery, partial and split payment |
| 13 | Order management for online orders: confirmation, allocation, fulfilment tracking, cancellation |
| 14 | Stock exposure policy: what stock is sellable online, from which locations, with what buffer |
| 15 | **Returns and RMA**: request, eligibility, authorisation, collection, inspection, disposition, refund |
| 16 | Promotions and vouchers at checkout (applied through M11, defined by M10/M35) |
| 17 | Loyalty points earn and redeem at checkout |
| 18 | Corporate/B2B commerce: contract pricing, approval chains, purchase-order reference, credit terms |
| 19 | Abandoned-cart recovery and browse-abandonment signals |
| 20 | Storefront content: banners, landing pages, campaign pages, policy pages |
| 21 | Conversion analytics: funnel, search, product, channel and cohort |
| 22 | Storefront SEO, structured data and shareable product links |
| 23 | The commerce API consumed by the web storefront, the mobile app and the corporate portal |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Third-party seller listings, seller onboarding, commission, payouts, disputes | **M12** Marketplace | Different seller, different liability, different VAT treatment |
| Item definitions, attributes, media, compatibility data | **M37** Catalogue | M38 renders a published catalogue; it does not define it |
| Prices, discounts, promotions calculation | **M11** Pricing | M38 displays; M11 decides |
| Promotion and campaign *definition*, vouchers, loyalty rules | **M10** Loyalty / **M35** Marketing | M38 is a redemption surface |
| Stock levels, reservation, picking, packing | **M15** Inventory / **M41** Warehouse | M38 requests; inventory holds |
| Physical delivery, courier assignment, POD | **M03** Logistics | M38 raises the consignment request |
| Invoice, receipt, refund posting, receivable | **M20** Receivable | Only Category G creates financial documents |
| Payment gateway contracts, settlement, reconciliation | **M50** Treasury / **M20** | M38 orchestrates the payment; finance settles it |
| VAT rates and filing | **M51** Tax | M38 presents; M51 computes |
| Refurbishment grading, reconditioning, unit preparation | **M14** Trade-In & Refurbishment | M38 sells the graded unit |
| Rental asset custody, condition, utilisation, damage | **M13** Rental | M38 takes the booking |
| Service execution after an online booking | **M01** SRM | The booking becomes a service order |
| Protection plan policy issue and claims | **M09** Warranty | M38 sells; M09 administers |
| The corporate website and its CMS | *Separate programme (OOS-01)* | The ERP provides commerce APIs; the marketing site is not built here |
| Customer identity, addresses, consent | **M33** Party Master | Referenced, never mastered |

### 3.3 Shared Concepts

| Concept | M38's Role | Owning Module |
|---|---|---|
| Published catalogue | Consumes the storefront projection | M37 |
| Price and promotion | Requests; never computes | M11 |
| Cart and checkout session | **Owner** | M38 |
| Online order | **Owner** until fulfilment handoff | M38 |
| Stock availability | Reads; owns the online exposure policy | M15 (stock) / M38 (exposure) |
| Payment | Orchestrates; M20 records | M38 (orchestration) / M20 (accounting) |
| Return / RMA | **Owner** of the commerce return; M03 moves goods; M15 receives | M38 |
| Service booking | Creates; M01 owns the resulting service order | M38 → M01 |
| Loyalty points | Applies at checkout | M10 |
| Refurbished unit | Sells; M14 grades and prepares | M14 |
| Storefront content | **Owner** of commerce content; marketing site is separate | M38 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **MACH / composable commerce** (commercetools, Elastic Path, Virto class) | Microservices, API-first, cloud-native, headless — the commerce engine exposed as APIs, the presentation layer independent | **Headless separation**: the ERP owns cart, pricing, inventory and order; the Next.js storefront and the React Native app are two heads on one commerce API. This is the only way P01 web, P01 app and P04 corporate can share one checkout | Full microservice decomposition — one commerce service inside the ERP is correct at our scale; a nine-service composable stack is not |
| **BigCommerce / Shopify headless** | Storefront APIs, cart and checkout as services, webhooks to ERP | The **storefront API contract shape** and the discipline that no business rule executes client-side | A SaaS commerce platform — it would take ownership of price, stock and order away from the ERP, violating principle 1 (one system of record) |
| **SAP Commerce Cloud** — B2B commerce | Contract pricing, account hierarchies, approval chains, quote-to-order, punchout | **B2B commerce as a first-class mode**: contract prices, multi-level approval, PO reference and credit terms in the same checkout | SAP Commerce's licence and complexity |
| **Oracle / Dynamics 365 Commerce** | Unified commerce across channel, click-and-collect, endless aisle | **Click-and-collect at 51+ branches** and **endless aisle** — a branch can sell stock held anywhere in the network. This is a genuine competitive advantage of having 51+ physical locations | Their POS coupling; branch counter sale stays in M04 |
| **Amazon / Daraz-class returns practice** | Self-service return request, eligibility windows, authorisation, collection, inspection, disposition, refund | The **RMA lifecycle with inspection-before-refund**, which is essential for electronics where "faulty" often means "user error" | Instant no-questions refunds — inappropriate for high-value electronics in this market |
| **Automotive parts e-commerce** (RockAuto, Partsouq class) | Vehicle/model-based fitment filtering as the primary navigation | **Device-compatibility filtering as the primary navigation for parts** — customers search by their device, not by part number. This is the single highest-impact conversion decision in the module | Their density-over-clarity interface conventions |
| **Odoo 19 + OCA** — `website_sale`, `website_sale_stock`, `website_sale_product_brand`, `website_sale_wishlist` | Product catalogue, cart, checkout, payment acquirer framework, order flow | The **order and payment-acquirer plumbing** as the L1/L2 base, driven through APIs rather than through Odoo's own front end | Odoo's website theming as the customer-facing storefront — it cannot meet the 3G payload, Bengali typography and app-parity requirements |

**Design position.** 1000FiX differs from the benchmarks in six ways.

First, **the storefront sells services as easily as goods**. Most commerce platforms treat a
bookable service as an awkward add-on. Here, a repair appointment, a rental hire and an AMC
package sit in the same cart as a charger, because that is how the customer thinks. The cart is
mixed-type by design and the checkout branches only where it must (slot selection, terms
acceptance, deposit).

Second, **compatibility filtering is the navigation**. A customer does not know their laptop's
battery part number. They know the model. The storefront's primary entry point is "tell us your
device", backed by M37's model-compatibility matrix, and everything else follows from it.

Third, **the 3G budget is a hard requirement, not an aspiration**. Critical paths must render
under 400 KB first load *(cross-portal standard PS-07)*. This constrains imagery, fonts and
JavaScript, and it is the reason for headless rather than a themed monolith.

Fourth, **stock exposure is a governed policy, not a switch**. Selling online from 51+ branch
stocks risks promising a part that a walk-in customer buys an hour later. M38 owns an exposure
policy — which locations, which buffer, which lead-time promise — and it is a commercial
decision reviewed regularly, not a technical default.

Fifth, **cash on delivery is a first-class payment method with fraud controls**. In this market
COD is not an edge case; it is a dominant preference. It also carries a real failure rate, so
COD eligibility is scored, limited by value and history, and its refusal rate is a tracked KPI.

Sixth, **the storefront is a surface, not a system**. It holds no authoritative state
*(portal principle PS-01…PS-12)*. Every price, stock check, tax computation and order transition
happens in the ERP. The client validates for convenience only.

---

## 5. Functional Areas & Features

### 5.1 Catalogue, Search & Merchandising

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ECM-001 | Storefront catalogue | Render the M37 storefront publication, honouring channel applicability, restrictions and completeness rules | P0 | L5 |
| FR-ECM-002 | Bilingual product content | Present name, description, specification and policy content in Bengali and English, with Bengali as default | P0 | L5 |
| FR-ECM-003 | Search | Provide typo-tolerant, bilingual search across name, alias, part number, brand and model, with ranked results in ≤ 300 ms | P0 | L5 |
| FR-ECM-004 | Faceted navigation | Filter by category, brand, model, price band, availability, grade, rating and delivery option | P0 | L5 |
| FR-ECM-005 | Device-compatibility filtering | Let a customer select or register their device and see only compatible parts and accessories, using the M37 compatibility matrix | P0 | L5 |
| FR-ECM-006 | Product detail | Present media, specification, compatibility, warranty terms, delivery options, availability and return policy on one page | P0 | L5 |
| FR-ECM-007 | Refurbished disclosure | For refurbished units, disclose the grade, its objective criteria, cosmetic condition photographs of the actual unit, and the warranty granted | P0 | L5 |
| FR-ECM-008 | Merchandising collections | Curate collections, featured sets and campaign landing pages, scheduled and audience-targeted | P1 | L5 |
| FR-ECM-009 | Cross-sell and up-sell | Present companion items, protection plans and higher grades contextually on product and cart pages | P1 | L5 |
| FR-ECM-010 | Recommendations | Serve recommendations from M26 (viewed-together, bought-together, device-based) with a rule-based fallback | P2 | L5 |
| FR-ECM-011 | Ratings and reviews | Collect, moderate and display verified-purchase reviews with photographs, in both languages | P2 | L5 |
| FR-ECM-012 | Wishlist and saved items | Save items, notify on price change or restock | P2 | L2 |
| FR-ECM-013 | SEO and sharing | Emit structured data, canonical URLs, sitemaps and shareable product links | P1 | L5 |
| FR-ECM-014 | Stock exposure policy | Apply a governed policy determining which locations, quantities and buffers are exposed online, with a per-item override | P0 | L5 |

### 5.2 Cart & Checkout

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ECM-015 | Persistent mixed cart | Maintain a persistent, cross-device cart holding goods, services, plans, rentals and bookings together | P0 | L5 |
| FR-ECM-016 | Live pricing and totals | Price every cart line and total through M11, including promotions, loyalty benefits and tax presentation | P0 | L5 |
| FR-ECM-017 | Availability validation | Re-validate availability, price and eligibility at cart entry, at checkout start and at order placement | P0 | L5 |
| FR-ECM-018 | Guest and account checkout | Support guest checkout with phone-OTP identification, and account checkout with saved addresses and methods | P0 | L5 |
| FR-ECM-019 | Address and location | Capture or select a delivery address with GPS pin, validate serviceability, and surface the applicable delivery options | P0 | L5 |
| FR-ECM-020 | Delivery mode selection | Offer home delivery, branch pickup (click-and-collect at 51+ branches), scheduled slot and express, with cost and promise date per option | P0 | L5 |
| FR-ECM-021 | Endless aisle | Sell an item held at any network location, with the promise date reflecting the transfer time | P1 | L5 |
| FR-ECM-022 | Voucher and promotion entry | Accept and validate a voucher or promotion code through M11/M10, showing the benefit before payment | P1 | L5 |
| FR-ECM-023 | Loyalty at checkout | Show points earnable, allow redemption within policy, and reflect the effect on the total | P1 | L5 |
| FR-ECM-024 | Payment orchestration | Offer bKash, Nagad, card, bank transfer and cash on delivery; support partial and split payment; handle authorisation, capture, failure and retry | P0 | L5 |
| FR-ECM-025 | COD governance | Score COD eligibility by customer history, order value and area; apply limits; require OTP confirmation above a threshold | P0 | L5 |
| FR-ECM-026 | Terms acceptance | Capture explicit acceptance of item-specific terms — refurbished condition, rental terms, protection plan wording, data-handling consent | P0 | L5 |
| FR-ECM-027 | Order confirmation | Confirm with an order number, itemisation, promise date and tracking link, delivered by app, SMS, WhatsApp and email | P0 | L5 |
| FR-ECM-028 | Checkout resilience | Never lose a cart or double-charge on network failure; payment and order placement are idempotent | P0 | L5 |
| FR-ECM-029 | Abandoned cart recovery | Detect abandonment, emit the signal to M35, and support a resume-cart link | P1 | L5 |
| FR-ECM-030 | Accessibility and performance | Meet WCAG 2.1 AA and keep the critical path under 400 KB first load on 3G | P0 | L5 |

### 5.3 Service, Plan & Rental Commerce

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ECM-031 | Service booking as a product | Present bookable services with indicative price from M11, delivery mode, duration and available slots | P0 | L5 |
| FR-ECM-032 | Slot selection | Show real capacity from M02/M55 by branch, skill and service type, and reserve the slot at order placement | P0 | L5 |
| FR-ECM-033 | Booking-to-service-order | Create the M01 service order on payment or confirmation, carrying device, fault description, photographs and channel | P0 | L5 |
| FR-ECM-034 | Pay-for-repair | Allow a customer to pay an issued repair invoice or approved quotation through the same checkout | P1 | L5 |
| FR-ECM-035 | Protection plan purchase | Sell protection products with eligibility checks from M09, inspection requirements surfaced, and policy issue on completion | P0 | L5 |
| FR-ECM-036 | Contract purchase and renewal | Sell and renew AMC/RAMC packages online, handing the accepted scope to M36/M08 | P1 | L5 |
| FR-ECM-037 | Rental booking | Show rental availability from M13, take the hire period, compute the deposit through M11, and capture terms acceptance | P2 | L5 |
| FR-ECM-038 | Trade-in at checkout | Offer a trade-in valuation from M14 against a purchase, applying it as a credit line | P2 | L5 |
| FR-ECM-039 | Subscription checkout | Sell subscription plans with the recurring charge, first-period proration and mandate set-up handled by M39 | P1 | L5 |

### 5.4 Order Management, Returns & RMA

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ECM-040 | Online order lifecycle | Own the order from placement through allocation, fulfilment handoff, delivery and closure | P0 | L5 |
| FR-ECM-041 | Allocation and sourcing | Allocate stock from the optimal location by availability, distance, cost and promise date, and raise the M15 reservation | P0 | L5 |
| FR-ECM-042 | Fulfilment handoff | Raise the M03 consignment or the branch pickup task, and track it to delivery | P0 | L5 |
| FR-ECM-043 | Order tracking | Present live status and tracking to the customer without login, via a tokenised link | P0 | L5 |
| FR-ECM-044 | Order modification | Allow address change, slot change and cancellation within policy windows, with automatic downstream unwinding | P1 | L5 |
| FR-ECM-045 | Partial fulfilment | Split an order across shipments and locations, with per-line status and per-shipment tracking | P1 | L5 |
| FR-ECM-046 | Return request | Accept a return request with reason, evidence photographs and preferred resolution, and evaluate eligibility against the policy | P0 | L5 |
| FR-ECM-047 | RMA authorisation | Authorise or refuse the return with a reason, issue an RMA number, and generate collection or drop-off instructions | P0 | L5 |
| FR-ECM-048 | Return inspection and disposition | Inspect on receipt against the declared reason, and disposition to restock, refurbish (M14), warranty claim (M09), scrap (M18) or refuse | P0 | L5 |
| FR-ECM-049 | Refund and exchange | Instruct M20 to refund to the original method, issue store credit, or process an exchange, only after inspection where policy requires | P0 | L5 |
| FR-ECM-050 | Return fraud control | Score return patterns — serial mismatch, excessive returns, evidence inconsistency — and route high scores for review | P1 | L5 |
| FR-ECM-051 | Warranty return routing | Route an in-warranty product return into the M09 claim path rather than a commercial refund where appropriate | P1 | L5 |

### 5.5 B2B Commerce & Analytics

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ECM-052 | Corporate commerce mode | Present contract pricing, agreed catalogue scope and credit terms to authenticated corporate users in P04 | P1 | L5 |
| FR-ECM-053 | Corporate approval chain | Route a corporate order through the client's own approval chain before it becomes a firm order | P1 | L5 |
| FR-ECM-054 | Purchase-order reference and bulk order | Capture the client's PO reference and support bulk order entry by CSV against the agreed catalogue | P1 | L5 |
| FR-ECM-055 | Conversion analytics | Instrument the full funnel — impression, product view, add to cart, checkout start, payment, order — by channel, device, campaign and cohort | P0 | L5 |
| FR-ECM-056 | Search and zero-result analytics | Report search terms, zero-result terms and search-to-purchase conversion, feeding catalogue and stocking decisions | P1 | L5 |

*(Full requirement text is mirrored in `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`.)*

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Headless commerce API** | One versioned commerce API serves the web storefront, the mobile app and the corporate portal. No head implements business logic *(PS-11)* |
| T-02 | **Idempotent order placement** | An order-placement request carries an idempotency key; retries and duplicate taps never create two orders or two charges |
| T-03 | **Payment state machine** | Authorisation, capture, failure, timeout, refund and chargeback are explicit states reconciled against the gateway, never inferred |
| T-04 | **Read-model catalogue** | The storefront reads a denormalised catalogue projection with a content hash, refreshed on M37 publication, never the transactional tables |
| T-05 | **Stock check freshness** | Availability is checked against M15 at cart entry, checkout start and placement, with the exposure buffer applied at each point |
| T-06 | **Reservation on placement, not on cart** | Stock is reserved at order placement, not when added to cart, with a declared hold period |
| T-07 | **3G performance budget** | Critical path first load ≤ 400 KB; product page LCP ≤ 2.5 s on a simulated 3G mid-range Android device |
| T-08 | **Image pipeline** | Images are served in modern formats at device-appropriate sizes from a CDN, with a low-quality placeholder strategy |
| T-09 | **Cart durability** | Carts survive session loss, device change and app reinstall, keyed to identity where known and to a durable token where not |
| T-10 | **Search index** | Bilingual, typo-tolerant index with synonym support for Bengali transliteration; index lag ≤ 60 s after catalogue publication |
| T-11 | **Tokenised public surfaces** | Tracking and return links are signed, expiring tokens exposing only the customer's own order |
| T-12 | **PCI posture** | No card data touches ERP systems; tokenised gateway integration only |
| T-13 | **Fraud signal isolation** | COD and return fraud scores are advisory inputs to a policy decision, always explainable, never a silent block |
| T-14 | **Event-driven fulfilment** | Every downstream action (reservation, consignment, service order, policy issue) is triggered by an outbox event, so a slow downstream never blocks checkout |
| T-15 | **Performance envelope** | Catalogue page ≤ 400 ms p95 API · search ≤ 300 ms p95 · cart operation ≤ 250 ms p95 · order placement ≤ 1.5 s p95 |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M38 |
|---|---|---|
| **Customer** | Must visit a branch to buy a charger or book a repair | Buys or books in under two minutes from a phone, in Bengali, with COD if preferred |
| **Branch staff** | Can only sell what is in their own branch | Sells from network stock via endless aisle; fulfils click-and-collect orders |
| **Inventory manager** | Slow-moving stock sits in one branch until written down | Exposes network stock to a national audience; ageing stock becomes sellable |
| **Refurbishment officer** | Refurbished units are sold ad hoc at the counter | Units are listed with grade, photographs and warranty, reaching customers nationally |
| **Marketing** | Runs campaigns with no measurable conversion path | Sees the funnel from impression to order, by campaign and cohort |
| **Corporate client** | Emails a parts order and waits for a quotation | Orders against agreed pricing through their own approval chain with a PO reference |
| **Contact centre agent** | Takes phone orders manually | Handles fewer transactional calls; supports customers through the same order record |
| **Finance officer** | Reconciles counter cash only | Reconciles gateway settlements against orders automatically |
| **CCO** | Has no digital sales channel to grow | Has a channel with measurable conversion levers |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Refurbished device resale** | A national storefront with grade disclosure and warranty, instead of counter-only sales | Enables the **BDT 65 lac/year** refurbishment and resale margin attributed to M14 |
| **Trade-in volume** | Trade-in offered at checkout against a purchase | Contributes to the same M14 benefit line by increasing device intake |
| **Spare parts and accessory retail** | Compatibility-filtered parts retail reaching customers who would never visit a branch for a BDT 400 cable | Grows revenue stream 5 beyond the counter; baseline to be established at launch |
| **Rental utilisation** | Online rental booking removes the friction of arranging a hire by phone | Supports the **BDT 48 lac/year** rental margin attributed to M13 |
| **Protection plan attach** | Plans offered at product checkout and at repair booking, not only at the counter | A principal channel for the **> 18% attach rate** target owned by M09 |
| **Online booking rate** | Booking a repair online instead of by phone or walk-in | Online booking rate **40% → 88%** *(P01 KPI)* |
| **Contact-centre deflection** | Self-service ordering, tracking and returns | Supports the **> 80% self-service status checks** target and reduces transactional call volume |
| **Working capital release** | Ageing and location-trapped stock becomes nationally sellable | Contributes to the **BDT 34 lac/year** inventory benefit attributed to M15 |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Reach beyond the branch footprint** | 51+ branches cover a fraction of Bangladesh. A storefront reaches customers where there is no branch, and tests demand before a branch is built |
| **Brand modernity** | A competent, fast, Bengali storefront changes how the company is perceived by younger customers and corporate buyers |
| **Price transparency** | Published prices online create external accountability for pricing consistency — reinforcing what M11 enforces internally |
| **Demand signal** | Search terms, zero-result searches and wishlist activity are direct demand data feeding M43 planning and M37 catalogue decisions |
| **Channel resilience** | A digital channel that operates when branches cannot (weather, strikes, disruption) is a continuity asset |
| **Foundation for the marketplace** | M12 launches on the same storefront, cart and checkout. Building M38 correctly halves the cost of M12 |
| **Accessibility** | WCAG 2.1 AA and a 3G budget mean the storefront works for customers on low-end devices and slow connections — the majority of the market |

---

## 8. Lifecycle & State Model

M38 owns the **online order** and the **return (RMA)**.

### 8.1 Online Order

```
   ┌──────┐  items added
   │ CART │  (persistent, not an order)
   └──┬───┘
      │ checkout started
   ┌──▼──────────┐
   │  CHECKOUT   │ address, delivery, terms, payment method
   └──┬──────────┘
      │ place order (idempotent)
   ┌──▼──────────────┐
   │ PAYMENT PENDING │──── failed / timeout ──► PAYMENT FAILED ──► retry or abandon
   └──┬──────────────┘
      │ authorised / captured / COD accepted
   ┌──▼──────────┐
   │  CONFIRMED  │  stock reserved; downstream events emitted
   └──┬──────────┘
      │ allocated from source location(s)
   ┌──▼──────────┐
   │  ALLOCATED  │
   └──┬──────────┘
      │ picked, packed, handed to M03 or branch
   ┌──▼──────────┐
   │ FULFILLING  │──► PARTIALLY FULFILLED (multi-shipment)
   └──┬──────────┘
      │ delivered / collected
   ┌──▼──────────┐
   │  DELIVERED  │
   └──┬──────────┘
      │ return window elapsed, no open RMA
   ┌──▼──────────┐
   │   CLOSED    │
   └─────────────┘

  Exceptions: CANCELLED (customer or 1000FiX, within policy) ·
              REFUSED (COD refused at door) · RETURNED (via RMA) ·
              ON HOLD (fraud review, stock exception, credit hold)
```

### 8.2 Return / RMA

```
   REQUESTED ──► ELIGIBILITY CHECK ──┬── refused ──► CLOSED (reason given)
                                     │
                                     └── eligible ──► AUTHORISED (RMA issued)
   AUTHORISED ──► IN TRANSIT (collection or drop-off) ──► RECEIVED
   RECEIVED ──► INSPECTED ──┬── accepted ──► DISPOSITIONED (restock / refurbish /
                            │                warranty claim / scrap)
                            │                        │
                            │                        ▼
                            │                  REFUNDED / EXCHANGED / CREDITED
                            │
                            └── rejected ──► RETURN TO CUSTOMER (reason + evidence)
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|
| Cart | Checkout | Every line still available, priced and eligible | Customer |
| Checkout | Payment Pending | Address serviceable; delivery mode chosen; terms accepted; COD eligibility passed if COD | Customer |
| Payment Pending | Confirmed | Payment authorised or captured, or COD accepted within limits | Payment gateway / system |
| Confirmed | Allocated | Stock reserved in M15 at the sourcing location(s) | System |
| Allocated | Fulfilling | Consignment raised in M03 or branch pickup task created | System |
| Fulfilling | Delivered | POD captured by M03, or collection confirmed at the branch | Rider / branch |
| Delivered | Closed | Return window elapsed with no open RMA | System |
| Any pre-fulfilment | Cancelled | Within the cancellation policy window; reservations released; payment refunded | Customer, agent |
| Delivered | Return Requested | Within the return window; item is return-eligible | Customer |
| Return Requested | Authorised | Eligibility passed; fraud score below the review threshold | System / agent |
| Received | Dispositioned | Inspection completed with evidence | Warehouse / branch |
| Dispositioned | Refunded | Refund instruction accepted by M20 | System |

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-ECM-01 | On M38 the seller is always 1000FiX; a third-party-supplied item can only be sold through M12 | **H** | CFO |
| BRU-ECM-02 | No price is computed by the storefront; every price and total comes from M11 | **H** | CTO |
| BRU-ECM-03 | Stock is reserved at order placement, never at cart addition | **C** | Inventory Manager |
| BRU-ECM-04 | Only stock within the governed online exposure policy may be sold online | **H** | Inventory Manager |
| BRU-ECM-05 | Order placement and payment are idempotent; no customer may be charged twice for one order | **H** | CTO |
| BRU-ECM-06 | A refurbished unit cannot be listed without its grade, its actual-unit photographs and its warranty terms | **H** | CCO |
| BRU-ECM-07 | Item-specific terms — refurbished condition, rental, protection plan, data handling — require explicit recorded acceptance | **H** | Legal / CCO |
| BRU-ECM-08 | COD is offered only within the declared eligibility policy and value limits | **H** | CFO |
| BRU-ECM-09 | A refund is issued only after inspection where the return policy requires inspection | **H** | CFO |
| BRU-ECM-10 | Refunds are made to the original payment method unless the customer accepts store credit | **H** | CFO |
| BRU-ECM-11 | A service booking becomes an M01 service order at confirmation; the booking never holds authoritative service state | **H** | Ops Director |
| BRU-ECM-12 | A protection plan sold online is not active until M09 eligibility and any required inspection are satisfied | **H** | CCO |
| BRU-ECM-13 | An in-warranty product fault is routed to the M09 warranty path, not treated as a commercial return, where the policy so provides | **C** | Warranty Officer |
| BRU-ECM-14 | Corporate orders follow the client's own approval chain before becoming firm orders | **H** | CCO |
| BRU-ECM-15 | The storefront implements no business rule client-side; the client validates for convenience only *(PS-11)* | **H** | CTO |
| BRU-ECM-16 | No card data is stored, processed or transmitted by ERP systems | **H** | CTO |
| BRU-ECM-17 | A customer-facing page must not exceed the 400 KB first-load budget on the critical path *(PS-07)* | **H** | CTO |
| BRU-ECM-18 | A return scored above the fraud threshold is reviewed by a human, never auto-refused | **A** | CCO |
| BRU-ECM-19 | An order on credit terms is placed only within the customer's available credit as reported by M33/M20 | **H** | CFO |
| BRU-ECM-20 | Every online order is traceable to one M20 financial document; no order is fulfilled without one | **H** | CFO |

*Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.cart` | `fix_cart` | Persistent cart | token, partner_id, channel, currency_id, state, last_activity_at, recovery_token |
| `fix.cart.line` | `fix_cart_line` | Cart lines | cart_id, line_type, item_id, variant_id, qty, price_snapshot, price_lock_ref, availability_state, config_json |
| `fix.online.order` | `fix_online_order` | The online order | name, cart_id, partner_id, channel, state, currency_id, total, delivery_mode, promise_date, payment_state, fraud_score, idempotency_key |
| `fix.online.order.line` | `fix_online_order_line` | Order lines | order_id, line_type, item_id, qty, unit_price, price_lock_id, source_location_id, fulfilment_state, service_order_ref, policy_ref |
| `fix.checkout.session` | `fix_checkout_session` | Checkout progress | cart_id, step, address_id, delivery_option, terms_accepted_json, payment_method, expires_at |
| `fix.payment.attempt` | `fix_payment_attempt` | Payment orchestration | order_id, method, gateway, gateway_ref, amount, state, attempt_no, failure_reason, at |
| `fix.stock.exposure.policy` | `fix_stock_exposure_policy` | Online sellability | item_id, category_id, location_ids, buffer_qty, buffer_pct, max_promise_days, enabled, approved_by |
| `fix.online.allocation` | `fix_online_allocation` | Sourcing decision | order_line_id, location_id, qty, reservation_ref, chosen_reason, promise_date |
| `fix.rma` | `fix_rma` | Return authorisation | number, order_id, partner_id, reason_code, requested_resolution, state, fraud_score, authorised_by, expires_at |
| `fix.rma.line` | `fix_rma_line` | Return lines | rma_id, order_line_id, qty, reason_code, evidence_ids, inspection_result, disposition, refund_amount |
| `fix.return.policy` | `fix_return_policy` | Eligibility rules | item_class, category_id, window_days, requires_inspection, restocking_fee, excluded_reasons_json |
| `fix.storefront.collection` | `fix_storefront_collection` | Merchandising sets | code, name_bn, name_en, rule_json, manual_item_ids, audience_json, valid_from, valid_to |
| `fix.storefront.content` | `fix_storefront_content` | Banners and pages | code, type, slot, content_bn, content_en, media_ids, audience_json, valid_from, valid_to |
| `fix.storefront.review` | `fix_storefront_review` | Ratings and reviews | item_id, order_line_id, partner_id, rating, text, media_ids, verified_purchase, moderation_state |
| `fix.commerce.funnel.event` | `fix_commerce_funnel_event` | Instrumentation | session_id, partner_id, event_type, item_id, channel, campaign_ref, at |
| `fix.search.query.log` | `fix_search_query_log` | Search analytics | query, language, result_count, clicked_item_id, converted, at |
| `fix.cod.eligibility` | `fix_cod_eligibility` | COD scoring | partner_id, score, max_value, area_risk, history_json, evaluated_at |

### 10.2 Referenced Entities

| Entity | Owned By | Access Pattern |
|---|---|---|
| Storefront catalogue publication, compatibility matrix, media | M37 | Publication event + read model |
| Price, promotion, voucher validation, loyalty benefit | M11 (via M10) | REST |
| Stock availability and reservation | M15 / M41 | REST + command |
| Party, addresses, consent, credit status | M33 | Live read |
| Invoice, receipt, refund, credit note | M20 | Command + events |
| Tax rates and treatment | M51 | REST |
| Consignment and delivery status | M03 | Command + events |
| Service order created from a booking | M01 | Command + events |
| Slot capacity | M02 / M55 | Live read |
| Protection product eligibility and policy issue | M09 | REST + events |
| Refurbished unit identity and grade | M14 | REST |
| Rental availability and terms | M13 | REST |
| Recommendations | M26 | Model output API |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-ECM-01 | M37 catalogue publication | Refresh the storefront read model and search index; invalidate CDN caches for changed items | Serve the previous version; alert Digital Squad |
| AUT-ECM-02 | Item added to cart | Validate availability, price and eligibility; annotate the line with any warning | Add the line flagged unavailable; never silently drop it |
| AUT-ECM-03 | Checkout started | Re-price the whole cart through M11, re-check availability, and show any change explicitly before payment | Block checkout with a clear explanation |
| AUT-ECM-04 | Order placed | Reserve stock, capture or authorise payment, emit `order.confirmed`, send confirmation on all preferred channels | Roll back the reservation; return a clear failure; never leave a partial order |
| AUT-ECM-05 | Order confirmed | Allocate from the optimal location, raise the M03 consignment or branch pickup task | Hold as an allocation exception; alert fulfilment |
| AUT-ECM-06 | Order line is a service booking | Create the M01 service order with device, description, photographs, slot and channel | Hold the line; alert the branch; never confirm a slot that was not reserved |
| AUT-ECM-07 | Order line is a protection plan | Instruct M09 to issue the policy after eligibility and any inspection requirement | Hold policy issue; notify the customer of the pending step |
| AUT-ECM-08 | Payment fails or times out | Retry per policy, preserve the cart, notify the customer with a resume link, release reservations after the hold period | Release reservations; log |
| AUT-ECM-09 | Cart abandoned beyond threshold | Emit the abandonment signal to M35 with a resume token | Log |
| AUT-ECM-10 | Delivery completed (M03 POD) | Move the order to Delivered, start the return window, trigger the review request | Retry; reconcile nightly |
| AUT-ECM-11 | COD order placed | Score eligibility, apply limits, require OTP above the threshold, and flag high-risk orders for confirmation call | Refuse COD with an explanation and offer prepaid |
| AUT-ECM-12 | Return requested | Evaluate eligibility and fraud score; authorise or route for review; issue the RMA and collection instruction | Route to manual review |
| AUT-ECM-13 | Return received | Create the inspection task; block refund until inspection completes where policy requires | Escalate after the inspection SLA |
| AUT-ECM-14 | Return inspected and accepted | Disposition the unit, instruct M20 to refund or credit, notify the customer | Hold; escalate to the returns officer |
| AUT-ECM-15 | Stock falls below the exposure buffer | Withdraw the item from online sale automatically and notify Inventory | Log; retry |
| AUT-ECM-16 | Restock of a wishlisted or back-in-stock item | Notify the customers who asked to be told | Log |
| AUT-ECM-17 | Zero-result search recurs beyond threshold | Raise a catalogue or stocking signal to M37 and M43 | Log |
| AUT-ECM-18 | Corporate order placed | Route through the client's approval chain; hold as a pending order until approved | Notify the corporate admin; expire per policy |

---

## 12. Interfaces

### 12.1 Upstream — M38 Consumes

| Source | What | Mechanism |
|---|---|---|
| M37 Catalogue | Storefront publication, media, compatibility matrix, refurbished grade definitions | Event `catalogue.published` + read model |
| M11 Pricing | Prices, promotions, voucher validation, cart totals | REST |
| M10 Loyalty | Points earn/redeem rules, vouchers, member benefits | REST (applied through M11) |
| M15 Inventory · M41 Warehouse | Availability by location, reservation, lead times | REST + command |
| M33 Party Master | Identity, addresses, consent, credit status, preferences | Live read |
| M09 Warranty | Protection product eligibility, policy issue, warranty status | REST + events |
| M14 Refurbishment | Refurbished unit identity, grade, actual-unit photographs, warranty | REST |
| M13 Rental | Rental availability, hire terms, deposit basis | REST |
| M02 / M55 | Service slot capacity | Live read |
| M03 Logistics | Delivery options, cost, promise dates, tracking, POD | REST + events |
| M20 Receivable | Invoice, receipt, refund and credit outcomes | Command + events |
| M51 Tax | Tax treatment for display and document | REST |
| M26 AI/ML | Recommendations, search ranking, fraud scores | Model output API |

### 12.2 Downstream — M38 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M01 SRM | Service orders created from online bookings, with full context | Command + event `order.service_booked` |
| M15 Inventory | Reservations, allocations, return receipts | Command |
| M03 Logistics | Consignment requests for delivery and return collection | Command |
| M20 Receivable | Order financial documents, payments, refunds, credits | Command |
| M09 Warranty | Protection plan sales for policy issue; warranty-routed returns | Events |
| M39 Subscription | Subscription plan sales for schedule creation | Event `order.subscription_purchased` |
| M08 Contract | Contract purchases and renewals accepted online | Event |
| M14 Refurbishment | Sold units, trade-in intents, returns dispositioned to refurbishment | Events |
| M13 Rental | Rental bookings | Command |
| M35 Marketing | Funnel events, abandoned carts, browse signals, campaign attribution | Events + warehouse |
| M43 Demand Planning | Demand signals, zero-result searches, wishlist and back-in-stock demand | Warehouse extract |
| M53 Revenue | Online revenue by stream with principal treatment declared | Projection |
| M25 BID · M26 AIM | Full commerce fact stream | Warehouse extract |
| **P01 Customer Portal & App** | The storefront itself — catalogue, cart, checkout, orders, returns | Commerce API |
| **P04 Corporate Portal** | B2B commerce mode | Commerce API |

### 12.3 Domain Events Published

| Event | Payload Summary | Principal Consumers |
|---|---|---|
| `cart.abandoned` | cart id, value, items, recovery token | M35, M27 |
| `order.placed` | order id, customer, channel, value, lines | M20, M15, M25 |
| `order.confirmed` | order id, payment state, promise date | M15, M03, M01, M27 |
| `order.service_booked` | order id, line, service, device, slot, branch | M01, M02 |
| `order.subscription_purchased` | order id, plan, term, customer | M39, M08 |
| `order.protection_purchased` | order id, product, device, customer | M09 |
| `order.allocated` | order id, lines, locations, promise dates | M15, M03 |
| `order.fulfilled` / `order.delivered` | order id, shipments, POD refs | M20, M27, M34 |
| `order.cancelled` | order id, reason, refund instruction | M15, M03, M20 |
| `rma.requested` | rma id, order, reason, items | M03, M15, M27 |
| `rma.authorised` | rma id, collection instruction, expiry | M03, M27 |
| `rma.dispositioned` | rma id, disposition, refund amount | M20, M15, M14, M09, M18 |
| `commerce.zero_result_search` | query, language, frequency | M37, M43 |
| `commerce.stock_withdrawn` | item, reason, locations | M15, M37 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-ECM-01 | bKash | Bidirectional | Payment authorisation, capture, refund, settlement callback |
| INT-ECM-02 | Nagad | Bidirectional | As above |
| INT-ECM-03 | SSLCOMMERZ (card and aggregated methods) | Bidirectional | As above |
| INT-ECM-04 | Bank transfer / IBFT confirmation *(via M50)* | Inbound | Payment confirmation for bank-transfer orders |
| INT-ECM-05 | Courier partner tracking *(via M03)* | Inbound | Delivery status for customer-facing tracking |
| INT-ECM-06 | CDN and object storage | Outbound | Media delivery within the performance budget |
| INT-ECM-07 | Corporate website / Next.js platform *(OOS-01 boundary)* | Outbound | Commerce API consumed by the marketing site |
| INT-ECM-08 | Analytics and tag platform | Outbound | Funnel instrumentation, with consent honoured |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/commerce/catalogue` | GET | Storefront catalogue with facets | P01, P04, website |
| `/api/v1/commerce/search` | GET | Bilingual, typo-tolerant search | P01, P04 |
| `/api/v1/commerce/compatibility` | POST | Compatible items for a device or model | P01 |
| `/api/v1/commerce/items/{id}` | GET | Product detail with availability and delivery options | P01, P04 |
| `/api/v1/commerce/cart` | GET/POST/PATCH | Cart operations | P01, P04 |
| `/api/v1/commerce/checkout` | POST | Start checkout, set address, delivery and payment method | P01, P04 |
| `/api/v1/commerce/checkout/slots` | GET | Available service or delivery slots | P01 |
| `/api/v1/commerce/orders` | POST | Place an order (idempotent) | P01, P04 |
| `/api/v1/commerce/orders/{id}` | GET | Order detail and status | P01, P04 |
| `/api/v1/commerce/orders/{id}/cancel` | POST | Cancel within policy | P01, P04 |
| `/api/v1/public/track/{token}` | GET | Tokenised order tracking without login | Unauthenticated |
| `/api/v1/commerce/returns` | POST | Request a return | P01, P04 |
| `/api/v1/commerce/returns/{id}` | GET | RMA status and instructions | P01, P04 |
| `/api/v1/commerce/payments/callback` | POST | Gateway callback (signed) | Payment gateways |
| `/api/v1/commerce/b2b/orders` | POST | Corporate order with PO reference and approval routing | P04 |
| `/api/v1/commerce/analytics/funnel` | GET | Funnel and conversion analytics | P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R04 Chief Commercial Officer | C R U D A | All |
| R23 Marketing Manager | C R U | Merchandising, content, collections, campaigns |
| R25 Retail / Refurbishment Officer | C R U | Refurbished listings, grades, unit photographs |
| R17 Inventory Manager | R U A | Stock exposure policy and buffers |
| R24 Marketplace Operations Officer | R | Shared storefront context *(M12 owns seller listings)* |
| R06 Branch Manager | R U | Own branch — click-and-collect fulfilment, endless-aisle orders |
| R08 Service Centre Agent | R U | Own branch — assisted ordering, pickup handover |
| R15 Logistics Coordinator | R U | Fulfilment and return collection |
| R26 Finance Manager | R A | Refund approval above threshold, COD policy, payment reconciliation |
| R27 Finance Officer | R U | Payment and refund processing |
| R34 Contact Centre Agent | C R U | Assisted ordering, order and return support |
| R32 Quality Manager / ISO Coordinator | R | Review moderation policy, return quality signals |
| R33 IT / System Administrator | R U | Storefront configuration, integrations, performance |
| R36 Customer | C R U | Own cart, orders and returns |
| R37 Corporate Portal User | C R U | Own company; role-scoped; approver may authorise orders |
| — Returns Officer *(new position under R25)* | C R U | RMA inspection and disposition |

**Field-level restrictions.** Cost, margin, sourcing location economics and internal fraud scores
are never exposed on any customer surface. `internal_note` is never exposed externally
*(EA-02)*. Payment credentials are never held by the ERP.

**Segregation of duties.** SOD-17 *(to be registered in `05-04` §6)*: the officer who inspects a
return cannot approve a refund above the threshold, complementing SOD-04.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Conversion funnel | CCO, Marketing, Digital Squad | Daily | Impression → view → add to cart → checkout → payment → order, by channel, device, campaign and cohort |
| Revenue and margin by stream | CCO, CFO | Weekly | Online revenue and margin by parts, accessories, refurbished, plans, bookings and rental |
| Search and zero-result analysis | CCO, Catalogue Officer, Demand Planning | Weekly | Top searches, zero-result terms, search-to-purchase conversion |
| Cart abandonment | Marketing, CCO | Daily | Abandonment rate and value by stage, with recovery performance |
| Delivery promise performance | Logistics Manager, CCO | Weekly | Promised vs actual delivery, by mode, zone and courier |
| Payment method performance | CFO, Digital Squad | Weekly | Success rate, failure reasons and cost by method; COD refusal rate |
| COD risk report | CFO, CCO | Weekly | COD orders by value band and area, refusal rate, loss value |
| Returns and RMA analysis | CCO, Quality Manager, Inventory Manager | Weekly | Return rate and value by reason, item and channel; disposition mix; inspection cycle time |
| Return fraud signals | CCO, Finance Manager | Monthly | High-scoring patterns and review outcomes |
| Stock exposure effectiveness | Inventory Manager, CCO | Weekly | Exposed vs sold, stockouts caused, buffer breaches, endless-aisle fulfilment |
| Refurbished sell-through | Retail Officer, CCO | Weekly | Listing-to-sale time by grade, model and price band |
| Storefront performance | CTO, Digital Squad | Daily | Page weight, LCP, API latency, error rate, availability on 3G profile |
| Review and rating summary | CCO, Quality Manager | Monthly | Rating distribution by item and category; moderation queue |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W8 Target | W9 Target |
|---|---|---|---|---|
| KPI-C38-01 | Online booking rate (services) | 40% | 75% | **88%** |
| KPI-C38-02 | Checkout funnel conversion | unmeasured | 60% | **> 72%** |
| KPI-C38-03 | Cart abandonment rate | n/a | < 55% | **< 42%** |
| KPI-C38-04 | Critical-path first load on 3G | n/a | ≤ 450 KB | **≤ 400 KB** |
| KPI-C38-05 | Product page LCP on a mid-range Android over 3G | n/a | ≤ 3.0 s | **≤ 2.5 s** |
| KPI-C38-06 | Order placement p95 latency | n/a | ≤ 2.0 s | **≤ 1.5 s** |
| KPI-C38-07 | Payment success rate (prepaid) | n/a | 92% | **> 96%** |
| KPI-C38-08 | COD refusal rate | n/a | < 12% | **< 6%** |
| KPI-C38-09 | Delivery promise attainment | n/a | 90% | **> 95%** |
| KPI-C38-10 | Return rate (value) | n/a | < 6% | **< 4%** |
| KPI-C38-11 | RMA inspection-to-refund cycle time | n/a | < 5 days | **< 2 days** |
| KPI-C38-12 | Protection plan attach at online checkout | 0% | 12% | **> 18%** |
| KPI-C38-13 | Refurbished listing-to-sale time | unmeasured | < 30 days | **< 14 days** |
| KPI-C38-14 | Zero-result search rate | n/a | < 8% | **< 3%** |
| KPI-C38-15 | Orders placed without any manual intervention | n/a | 92% | **> 98%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `website_sale`, `payment`, `sale`, `delivery` | 16% |
| L2 | OCA `website_sale_stock_available`, `website_sale_product_brand`, `website_sale_wishlist`, `sale_order_type`, `payment_*` | 14% |
| L4 | Next.js storefront and React Native commerce screens *(shared with P01)* | 26% |
| L5 | `cd_commerce_api`, `cd_cart_checkout`, `cd_service_booking_commerce`, `cd_returns_rma`, `cd_merchandising` | 44% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-C38-01 | `cd_commerce_api` — headless commerce API, catalogue read model, search index, tokenised public surfaces | Service | 6 PW |
| CD-C38-02 | `cd_cart_checkout` — persistent mixed cart, checkout state machine, idempotent placement, payment orchestration, COD governance | Odoo module + service | 8 PW |
| CD-C38-03 | `cd_service_booking_commerce` — bookable services, slot reservation, service-order creation, plan and rental commerce | Odoo module | 5 PW |
| CD-C38-04 | `cd_returns_rma` — return policy, RMA lifecycle, inspection, disposition, refund instruction, fraud scoring | Odoo module | 5 PW |
| CD-C38-05 | `cd_merchandising` — collections, content, cross-sell, reviews, stock exposure policy | Odoo module | 3 PW |
| CD-C38-06 | Storefront front-end integration and performance engineering *(with the P01 team)* | Front end | 3 PW |
| | | **Total** | **30 PW** |

> **Boundary note.** The Next.js storefront and React Native app shells are delivered by the
> P01 workstream under a separate line; the 3 PW above covers the commerce-specific integration
> and the 3G performance budget work, not the portal build. OOS-01 excludes the corporate
> website itself.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M37 Catalogue *(W1)* | There is nothing to sell without a published catalogue with compatibility data |
| M11 Pricing *(W3)* | Every displayed price comes from M11 |
| M15 Inventory *(W2)* · M41 Warehouse *(W3)* | Availability, reservation and fulfilment |
| M20 Receivable *(W3)* · M51 Tax *(W4)* | Financial documents and VAT |
| M03 Logistics *(W3)* | Delivery and return collection |
| M09 Warranty *(W4)* | Protection plan sale and policy issue |
| M10 Loyalty *(W2)* | Points and vouchers at checkout |
| M14 Refurbishment *(W6)* · M13 Rental *(W6)* | Refurbished and rental commerce depend on those modules being live |
| P01 Customer Portal *(W2, app W6)* | The storefront's principal head |

**M38 must be accepted before M12 Marketplace**, which extends the same storefront, cart and
checkout with third-party supply. Building them in the reverse order would duplicate the
commerce core.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Existing website product content (if any) | To be profiled | `fix.storefront.content`, media | W7 |
| Historical counter sales of parts/accessories (for demand baseline) | 24 months | Warehouse only | W7 |
| Refurbished stock on hand at launch | Per M14 | Listed from M37/M14, not migrated into M38 | W7 |

M38 holds no legacy transactional data; it is a new channel. The migration effort is content and
media preparation, and it is a marketing task with a hard deadline, not a data task.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A customer completes a parts purchase in under two minutes on a mid-range Android device over a throttled 3G connection, in Bengali | Timed field test, twenty samples, real customers |
| AC-02 | Critical-path first load ≤ 400 KB and product page LCP ≤ 2.5 s on the 3G profile | Performance test report |
| AC-03 | Device-compatibility filtering returns only parts that fit the selected model | Test matrix across ten device models |
| AC-04 | A mixed cart containing a part, a service booking and a protection plan checks out correctly, creating all three downstream objects | End-to-end demonstration |
| AC-05 | Order placement and payment are idempotent under retry, double-tap and network failure; no duplicate order or double charge occurs | Chaos test across all payment methods |
| AC-06 | Stock is reserved only at placement, and the exposure policy is respected at every stage | Negative test with concurrent counter sale |
| AC-07 | A refurbished unit cannot be listed without grade, actual-unit photographs and warranty terms | Negative test |
| AC-08 | COD eligibility, limits and OTP confirmation are enforced, and refusal offers a prepaid alternative | Test matrix by value band and history |
| AC-09 | A return is requested, authorised, collected, inspected and refunded end to end, with no refund before inspection where policy requires | Scripted scenario per policy variant |
| AC-10 | An in-warranty fault return routes to the M09 warranty path rather than a commercial refund | Scripted scenario |
| AC-11 | A corporate order routes through the client's approval chain and carries the PO reference to the invoice | Joint test with P04 and M20 |
| AC-12 | Every online order reconciles to exactly one M20 financial document and one gateway settlement line | Reconciliation report |
| AC-13 | No business rule executes client-side; disabling client validation cannot produce an invalid order | Security and API test |
| AC-14 | Named business super-users sign off UAT for all P0 and P1 requirements | Signed UAT record |
| AC-15 | Zero critical or high security findings, including on tokenised public surfaces and payment callbacks | Security review record |

**Definition of done:** all 17 criteria in `02-02` §8 plus the criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | What is the online stock exposure policy — all branches, selected hubs, or warehouse only — and who approves changes to it? | CCO / Inventory Manager | W7 build |
| Q-02 | What is the return window and restocking-fee policy per item class, and does it comply with Bangladeshi consumer protection rules? | Legal / CCO | W7 build |
| Q-03 | What COD value ceiling and area exclusions apply, and who bears the loss on refusal? | CFO / Logistics Manager | W7 build |
| Q-04 | Does 1000FiX intend to sell on external marketplaces (Daraz and similar) in addition to its own storefront? That is a channel decision with M38 integration consequences | CEO / CCO | W7 planning |
| Q-05 | Who owns storefront merchandising day to day — Marketing or Commercial? | CCO / Marketing Head | W7 build |
| Q-06 | Is the storefront hosted on the corporate Next.js platform (OOS-01) or on ERP-adjacent infrastructure? The performance budget and deployment model depend on it | CTO | **W6 — blocking** |
| Q-07 | What is the warranty position on a refurbished unit sold online and returned outside the return window but inside the warranty period? | CCO / Warranty Officer | W7 build |
| Q-08 | Are online prices permitted to differ from branch prices, and within what spread? *(cross-reference M11 Q-02)* | CCO | W7 build |

---

## 19. References

**Internal**
`03_Modules/C_Commercial_Pricing_and_Revenue/_CATEGORY_OVERVIEW.md` §4.3, §10 ·
`M37_Product_and_Service_Catalogue_Management.md` §5.6 (channel publication) ·
`M11_Pricing_Rate_Cards_and_Dynamic_Pricing.md` §5.1, §5.4 ·
`M09_Warranty_Protection_Plans_and_Claims.md` §5.2 ·
`M39_Subscription_and_Recurring_Revenue.md` §3 ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`05-04_Role_Permission_and_Access_Matrix.md` §5, §8 ·
`05-06_NonFunctional_Requirements_and_Standards.md` ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` P01 §Shop, P04 §Procurement, §3 PS-07, PS-11 ·
`00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md` §3, §8 OOS-01 ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.12 ·
`1000FiX_ERP_System_Comprehensive_URD.md` §10 ·
`1000FiX Business Plan` §Refurbished Device Resale, §Spare Parts & Accessories, §Rental ·
`1000fix_business/SOW for 1000FiX Service App Development.docx` §Product Purchase

**External benchmark**
MACH / composable commerce architecture (commercetools, Elastic Path, Virto) — headless separation and API-first commerce ·
BigCommerce / Shopify headless storefront API practice ·
SAP Commerce Cloud B2B — contract pricing, account hierarchies, approval chains ·
Oracle / Dynamics 365 Commerce — unified commerce, click-and-collect, endless aisle ·
Marketplace returns practice (Amazon, Daraz) — RMA lifecycle with inspection before refund ·
Automotive parts e-commerce — fitment-based navigation as the primary discovery path ·
Odoo 19 `website_sale` and OCA website-sale module family

---

*Module M38 · Category C · 1000FiX ERP System v2.0 · CONFIDENTIAL*
