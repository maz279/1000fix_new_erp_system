---
id: FIX-ERP2-CAT-B
category: B
category_name: Customer Engagement & Experience
module_count: 7
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT
---

# Category B — Customer Engagement & Experience

**7 modules · Category owner: Chief Commercial Officer**

---

## 1. What Belongs in This Category

Who the customer is, how we come to know them, how we talk to them, and how they feel about
the result.

If a capability answers *"who is this party, what have we said to them, and what do they
think of us"*, it belongs here. If it answers *"what did we agree to sell them"* or
*"what work are we doing"*, it does not.

---

## 2. Modules

| ID | Module | Status | Pri | Wave | Reqs | Effort | One-Line Definition |
|---|---|---|:--:|:--:|---:|---:|---|
| **M33** | [Customer & Party Master Management](M33_Customer_and_Party_Master_Management.md) ★ | New | P0 | W1 | 52 | 24 PW | The single authoritative record of every party — customer, corporate group, household, dealer, government body — with identity, hierarchy, addresses and consent |
| **M07** | [CRM, Sales Pipeline & Account Management](M07_CRM_Sales_Pipeline_and_Account_Management.md) | Re-scoped | P1 | W1 / W4 | 46 | 22 PW | Leads, opportunities, account plans, dedicated account managers and quarterly business reviews |
| **M10** | [Loyalty, Membership & Rewards](M10_Loyalty_Membership_and_Rewards.md) | Re-scoped | P1 | W2 | 44 | 18 PW | Privilege tiers, points, wallet, vouchers, referral mechanics and the loyalty liability |
| **M34** | [Customer Experience, Feedback & Complaints](M34_Customer_Experience_Feedback_and_Complaints.md) ★ | New | P1 | W4 | 42 | 17 PW | CSAT, NPS, CES, the closed feedback loop, and the customer-facing complaint process |
| **M27** | [Omnichannel Contact Centre & Communications](M27_Omnichannel_Contact_Centre_and_Communications.md) | Re-scoped | P1 | W4 † | 58 | 32 PW | Every inbound and outbound conversation across voice, chat, WhatsApp, email, SMS and social — and all notification delivery |
| **M32** | [Conversational AI & Virtual Assistant](M32_Conversational_AI_and_Virtual_Assistant.md) ★ | New | P1 | W4 ‡ | 38 | 18 PW | The Bengali-first AI assistant that handles first-line conversations and performs authenticated actions |
| **M35** | [Marketing, Campaigns & Demand Generation](M35_Marketing_Campaigns_and_Demand_Generation.md) ★ | New | P2 | W5 | 40 | 17 PW | Campaign planning and execution, journey orchestration, budget and marketing attribution |
| | | | | **Total** | **320** | **148 PW** | **All 7 specifications written** |

★ = new in v2.1 after enterprise benchmarking.

### Two Sequencing Issues Raised During Specification

**† M27 notification delivery should move from W4 to W1 or W2.** Every module from Wave 1
needs to notify customers. If M27 arrives in W4, each earlier module builds its own send path —
recreating the fragmentation the programme exists to remove, and putting consent enforcement
outside a single controlled layer. See `M27` §16.3 and Q-05.

**‡ M32 depends on M61 Knowledge, scheduled two waves later in W6.** An assistant without a
knowledge base can answer transactional questions from live ERP data, but not "how do I" or
"why is my device doing this" — a large share of real enquiries. Either M61 core content moves
to W4, or M32 launches with a reduced intent scope. See `M32` §16.3 and Q-01.

Both are **wave-plan decisions for `06-01`**, not design questions.

---

## 3. Why the Master Data Split (M33 vs M07)

This mirrors how every enterprise ERP separates **party master data** from **sales process**.

| | M33 Customer & Party Master | M07 CRM & Account Management |
|---|---|---|
| **Owns** | Identity, hierarchy, addresses, verification documents, consent, credit profile, party roles | Leads, opportunities, activities, account plans, account manager assignment, QBRs |
| **Analogue** | SAP *Business Partner* · Oracle *Trading Community Architecture* · Dynamics *Account/Contact in Dataverse* | SAP *Sales* · Oracle *Sales Cloud* · Dynamics 365 *Sales* |
| **Change driver** | Governance and data quality | Commercial pursuit |
| **Governed by** | Master data management (M64) | Sales process |
| **Consumers** | Every module in the system | Sales and account teams |

**Rule:** M33 owns the party record; every other module references it. M07 never creates or
edits master identity attributes — it raises a master-data change request to M33.

---

## 4. Why Conversational AI Is Separate (M32 vs M27)

| | M27 Contact Centre | M32 Conversational AI |
|---|---|---|
| **Owns** | Channels, queues, agent workspace, routing, telephony, notification delivery, transcripts | Intent understanding, dialogue management, knowledge grounding, authenticated actions, handoff decision |
| **Analogue** | Genesys / Dynamics 365 Contact Center | Purpose-built assistant layer |
| **Fails how** | Customer cannot reach a human | Assistant gives a wrong answer |
| **Governed by** | Service-level management | AI governance (M26 model policy) |

They are separate because their **failure modes, release cadence and governance differ**.
A telephony change must not require an AI model release, and vice versa.

---

## 5. Category Boundary Map

| Capability | Owned By | Not Owned By |
|---|---|---|
| Party identity, hierarchy, addresses | **M33** | M07, M12, M40 (all reference) |
| Consent and communication preference | **M33** | M27, M35 (both enforce, neither owns) |
| Credit limit and payment terms | **M33** holds; **M20** enforces | M07 |
| Customer-facing complaint intake and resolution communication | **M34** | M23 (owns the internal non-conformance) |
| Internal root cause and corrective action | **M23** | M34 |
| Notification template, channel and delivery | **M27** | Every module raises events; none sends |
| Campaign definition and execution | **M35** | M10 (supplies the offer mechanics) |
| Voucher, points, tier benefit mechanics | **M10** | M35 (uses them in campaigns) |
| Referral programme mechanics | **M10** | M40 (owns the partner relationship behind it) |
| Marketplace seller reviews | **M12** | M34 (owns customer-of-1000FiX feedback) |
| Model training and serving | **M26** | M32 (consumes) |
| Corporate contact roles and approval chains | **M33** | M07, P04 |

---

## 6. The Customer Data Ownership Rule

One rule prevents the most common ERP data disaster.

> **Every customer attribute has exactly one owning module. A module that displays an
> attribute it does not own must read it live or through an event projection — never store
> its own copy as truth.**

| Attribute Group | Owner |
|---|---|
| Name, type, identity documents, addresses, contacts | M33 |
| Consent and channel preference | M33 |
| Credit limit, payment terms, credit hold | M33 |
| Segment membership | M33 (definition) / M35 (campaign use) |
| Loyalty tier, points balance, wallet | M10 |
| Open opportunities and account plan | M07 |
| Satisfaction scores and complaint history | M34 |
| Conversation history | M27 |
| Contracts and entitlements | M08 |
| Devices and assets | M17 |
| Invoices, payments, balance | M20 |

---

## 7. Category KPIs

| KPI | Baseline | Target | Owning Module |
|---|---|---|---|
| Customer record completeness | unmeasured | > 92% | M33 |
| Duplicate customer rate | unmeasured | < 1% | M33 |
| Customer 360 load time | — | < 2 s | M33 |
| Corporate registration approval cycle | manual | < 24 h | M33 |
| CSAT | 3.8 / 5 | 4.7 / 5 | M34 |
| NPS | unmeasured | > 55 | M34 |
| Complaint resolution within SLA | unmeasured | > 95% | M34 |
| Conversations captured in system | ~0% | 100% | M27 |
| First-contact resolution (all channels) | unmeasured | > 78% | M27 |
| AI first-contact resolution | 0% | > 55% | M32 |
| Notification delivery success | unmeasured | > 98% | M27 |
| Privilege membership base | baseline | 3× | M10 |
| Campaign ROI | unmeasured | > 4 : 1 | M35 |
| Referral-attributed new customers | 0% | > 12% | M10 / M40 |
| Customer churn | ~15% | < 8% | M07 / M34 |

---

## 8. Category Delivery Sequence

```
W1   M33 Party Master ──┐
     M07 CRM ───────────┴──► customer known, pipeline running
W2   M10 Loyalty ───────────► Privilege programme live
W4   M27 Contact Centre ─┐
     M32 Conversational AI┤
     M34 Customer Experience──► every conversation and every score captured
W5   M35 Marketing ─────────► campaigns and demand generation
```

---

## 9. Category Risks

| Risk | Impact | Mitigation | Owning Module |
|---|---|---|---|
| Duplicate and fragmented customer records survive migration | Critical — undermines every downstream module | Profiling before load, supervised merge, ongoing duplicate detection | M33 |
| Consent handled inconsistently across channels | High — legal and reputational | One consent record, enforced at the point of send, never at the point of campaign design | M33 / M27 |
| The AI assistant answers wrongly on price or policy | High — commercial and trust damage | Knowledge grounding with citations; hard guard rails; never quote outside the price book | M32 |
| Complaints logged in two systems | High — nothing gets resolved | M34 owns customer-facing; M23 owns internal; one complaint object, two views | M34 / M23 |
| Marketing sends to customers who opted out | Critical — regulatory | Suppression is enforced in the delivery layer, not the campaign layer | M27 |

---

*Category B · 1000FiX ERP System v2.0*
