# REQUEST FOR PROPOSAL (RFP)

# Comprehensive Enterprise Resource Planning (ERP) System & Smart Portal Suite

# For 1000FiX Services Limited

---

| **Document Information** | |
|---|---|
| **Document Title** | Request for Proposal — Comprehensive ERP System & Smart Portal Suite |
| **Issuing Organization** | 1000FiX Services Limited |
| **Document Version** | 1.0 |
| **Date of Issue** | March 17, 2026 |
| **RFP Reference Number** | 1000FIX-ERP-RFP-2026-001 |
| **Submission Deadline** | May 15, 2026, 5:00 PM (BST, UTC+6) |
| **Contact Person** | Chief Technology Officer, 1000FiX Services Limited |
| **Contact Email** | info@1000fix.com |
| **Contact Phone** | +880 9644-300600 |
| **Address** | 586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216, Bangladesh |

---

**CONFIDENTIALITY NOTICE**

This Request for Proposal (RFP) document and all accompanying materials are the confidential property of 1000FiX Services Limited. The information contained herein is intended solely for the use of prospective vendors who have been invited to submit proposals. Recipients of this document must not disclose, reproduce, or distribute any part of this RFP without the prior written consent of 1000FiX Services Limited. All information provided by respondents will be treated as confidential and used solely for the purpose of evaluating proposals.

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Company Background & Overview](#2-company-background--overview)
3. [Project Scope & Objectives](#3-project-scope--objectives)
4. [Current IT Landscape & Pain Points](#4-current-it-landscape--pain-points)
5. [Functional Requirements](#5-functional-requirements)
   - 5.1 Service & Repair Management
   - 5.2 Field Service Management
   - 5.3 Inventory & Spare Parts Management
   - 5.4 Customer Relationship Management (CRM)
   - 5.5 Financial Management & Accounting
   - 5.6 Human Resource Management & Payroll
   - 5.7 Contract & Warranty Management
   - 5.8 Procurement & Supply Chain Management
   - 5.9 Reporting & Business Intelligence
   - 5.10 Document Management System
   - 5.11 Quality Management System
6. [Smart Portal Suite Requirements](#6-smart-portal-suite-requirements)
   - 6.1 Customer Self-Service Portal
   - 6.2 Technician Mobile Portal
   - 6.3 Admin Operations Portal
   - 6.4 Corporate B2B Portal
   - 6.5 Vendor & Partner Portal
   - 6.6 Analytics & Business Intelligence Dashboard
7. [Technical Requirements](#7-technical-requirements)
8. [Integration Requirements](#8-integration-requirements)
9. [Data Migration Requirements](#9-data-migration-requirements)
10. [Security & Compliance Requirements](#10-security--compliance-requirements)
11. [Implementation Approach & Timeline](#11-implementation-approach--timeline)
12. [Training & Change Management](#12-training--change-management)
13. [Support & Maintenance Requirements](#13-support--maintenance-requirements)
14. [Vendor Qualifications & Experience](#14-vendor-qualifications--experience)
15. [Budget & Pricing Structure](#15-budget--pricing-structure)
16. [Evaluation Criteria](#16-evaluation-criteria)
17. [Submission Guidelines & Instructions](#17-submission-guidelines--instructions)
18. [Terms & Conditions](#18-terms--conditions)
19. [Appendices](#19-appendices)

---

## 1. EXECUTIVE SUMMARY

### 1.1 Purpose of This RFP

1000FiX Services Limited ("1000FiX" or "the Company") is seeking proposals from qualified Enterprise Resource Planning (ERP) solution providers to implement a comprehensive, integrated ERP system coupled with a suite of smart portals to manage the Company's end-to-end business operations.

This RFP invites technology vendors, system integrators, and ERP solution providers to submit detailed proposals for the design, development, deployment, and ongoing support of an ERP platform that will serve as the operational backbone for Bangladesh's largest after-sales service provider.

### 1.2 Strategic Vision

1000FiX is undergoing a major digital transformation initiative to modernize its entire operational infrastructure. The Company currently operates 51+ service centers across all 8 administrative divisions of Bangladesh, employs hundreds of field service technicians, and manages thousands of service orders daily across IT equipment, mobile devices, and home appliances.

The proposed ERP system must:

- **Unify** all business operations under a single, integrated platform
- **Automate** at least 70% of repetitive operational processes
- **Enable** real-time visibility across all 51+ service center locations
- **Support** multi-channel service delivery (on-site, pick & drop, walk-in, remote)
- **Integrate** seamlessly with the Company's existing and in-development 8-portal smart web platform (built on Next.js 15 + Payload CMS 3 + PostgreSQL 16)
- **Scale** to support 250,000+ monthly users and 5x business growth over 5 years
- **Comply** with Bangladesh regulatory requirements including VAT, tax, and data privacy

### 1.3 Expected Business Outcomes

| Outcome | Current Baseline | Target |
|---|---|---|
| Operational automation | ~20% | 70%+ |
| Online booking rate | 40% | 85%+ |
| Technician productivity | 4-5 jobs/day | 7-8 jobs/day |
| First-time fix rate | 70% | 85%+ |
| Customer satisfaction | 3.8/5 | 4.7/5 |
| Support cost reduction | Baseline | -60% |
| Revenue growth | Baseline | +87% (18 months) |
| Order processing time | Manual | 80% automated |
| Inventory accuracy | ~75% | 98%+ |
| Financial close cycle | 15-20 days | 3-5 days |

### 1.4 Scope Summary

The ERP system must encompass the following core domains:

1. **Service & Repair Management** — End-to-end service order lifecycle
2. **Field Service Management** — Technician dispatch, scheduling, and mobile operations
3. **Inventory & Spare Parts** — Multi-location inventory across 51+ service centers
4. **CRM** — Customer, device, and relationship management
5. **Financial Management** — Multi-branch accounting, billing, and treasury
6. **HR & Payroll** — Workforce management for 500+ employees
7. **Contract & Warranty Management** — AMC, RAMC, brand warranty claims
8. **Procurement & Supply Chain** — Spare parts sourcing and vendor management
9. **Business Intelligence** — Real-time dashboards and analytics
10. **Document Management** — Digital forms, approvals, and archiving
11. **Smart Portal Suite** — 6 integrated web/mobile portals

---

## 2. COMPANY BACKGROUND & OVERVIEW

### 2.1 Company Profile

| Attribute | Details |
|---|---|
| **Legal Name** | 1000FiX Services Limited |
| **Trading Name** | 1000FiX |
| **Industry** | After-Sales Service / IT & Electronics Repair / Home Appliance Maintenance |
| **Founded** | August 29, 2017 |
| **Headquarters** | 586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216, Bangladesh |
| **Hotline** | 16743 (16 + Fix in Bangla) |
| **Phone** | 09644-300600 |
| **Email** | info@1000fix.com |
| **Website** | https://1000fix.com |
| **Certification** | ISO 9001:2015 (Bangladesh's first & only ISO-certified IT service provider) |
| **Service Centers** | 51+ across all 8 divisions of Bangladesh |
| **WhatsApp** | +880 1904 095968 |

### 2.2 Market Position

1000FiX holds a unique and dominant position in the Bangladesh market:

- **Largest** after-sales ICT, electronics, and home appliance service provider in Bangladesh
- **Only** ISO 9001:2015 certified IT service provider in the country
- **Authorized warranty service partner** for 17+ international brands
- **Most extensive service network** with 51+ centers covering all 8 administrative divisions
- **Multi-channel service delivery** including on-site, pick & drop, walk-in, and remote support

### 2.3 Authorized Brand Partnerships

1000FiX serves as the official authorized after-sales service partner for the following brands in Bangladesh:

| Category | Brands |
|---|---|
| **Computers & Laptops** | Dell, HP, Lenovo, Acer, Toshiba, Gigabyte, Microsoft (Surface) |
| **Consumer Electronics** | Samsung, Sony, BenQ |
| **Mobile Devices** | Xiaomi, Huawei, Honor |
| **Components** | Intel, TwinMOS, Delux |
| **Printers & Peripherals** | Epson |
| **Others** | PNS |

### 2.4 Service Portfolio

#### 2.4.1 IT Equipment Services
- Laptop & Notebook Repair (all brands, Level 1-3 repair)
- Desktop Computer Repair (brand & clone PCs)
- MacBook & Apple Product Repair (specialized Apple technicians)
- Server Repair & Maintenance
- Printer, Photocopier & Plotter Services
- Motherboard-Level Repair & Diagnostics
- Monitor & Display Repair
- Projector Services
- UPS Repair & Maintenance
- Router & Networking Equipment Services
- CCTV & Surveillance System Services
- Microsoft Surface Repair

#### 2.4.2 Home Appliance Services
- Air Conditioning — Installation, jet wash, hydraulic service, dismantling, gas refill, water drop/leakage repair, basic servicing
- Refrigerator — Servicing, repair, cleaning, gas refill, installation
- Television — All types and brands, display repair, technical repair
- Washing Machine — Overhauling, repair, maintenance
- Microwave & Oven — Repairing, display problem solutions
- Geyser/Water Heater — Repair & winter maintenance
- Treadmill — Fitness equipment repair
- Combo Service Packages (AC + Refrigerator bundles)

#### 2.4.3 Mobile & Tablet Services
- Mobile Phone Repair (Samsung, Xiaomi, Huawei, Honor, others)
- Tablet Repair Services
- Speaker Repair
- Warranty and out-of-warranty support

#### 2.4.4 Service Delivery Methods
1. **On-Site / Home Service** — Technician visits customer location
2. **Pick & Drop Service** — Device pickup from customer, return after repair
3. **Service Center Walk-In** — Direct visits to any of 51+ service centers
4. **Remote PC Support** — Remote diagnostics and software support

#### 2.4.5 Value-Added Programs
- **Privilege Program** — Silver, Gold, Diamond membership tiers (50% off service charges)
- **Residential Annual Maintenance Contract (RAMC)** — 6 packages for periodic home appliance maintenance
- **Corporate AMC** — Annual maintenance contracts for businesses
- **Warranty Extension Program** — Extended protection beyond manufacturer warranty
- **Partner Alliance Program** — B2B corporate rates and bulk services
- **Laptop Rental Service** — Short-term device rental
- **Device Exchange Offer** — Trade-in programs for device upgrades

### 2.5 Organizational Structure

| Department / Function | Description | Estimated Users |
|---|---|---|
| **Executive Management** | C-suite, directors, strategic planning | 5-10 |
| **Service Operations** | Service order management, dispatch, quality control | 30-50 |
| **Field Service Technicians** | On-site repair, pick & drop, installations | 200-400 |
| **Service Center Staff** | Walk-in service center operations (51+ locations) | 150-250 |
| **Customer Service** | Call center, hotline (16743), WhatsApp support | 30-50 |
| **Inventory & Warehouse** | Spare parts management, procurement | 20-30 |
| **Finance & Accounting** | Billing, payments, collections, reporting | 15-25 |
| **Human Resources** | Recruitment, payroll, training, compliance | 10-15 |
| **Sales & Marketing** | Corporate sales, partnerships, marketing | 15-25 |
| **IT & Development** | Infrastructure, software, digital platforms | 10-15 |
| **Quality Assurance** | ISO compliance, audit, process improvement | 5-10 |
| **Corporate / B2B Sales** | Enterprise account management | 10-15 |
| **Total Estimated Users** | | **500-900** |

### 2.6 Geographic Coverage

1000FiX operates across all 8 administrative divisions of Bangladesh:

| Division | Key Cities | Service Centers |
|---|---|---|
| **Dhaka** | Dhaka, Gazipur, Narayanganj, Savar, Tangail, Manikganj | Headquarters + Multiple Centers |
| **Chittagong** | Chittagong, Cox's Bazar, Comilla, Noakhali | Multiple Centers |
| **Rajshahi** | Rajshahi, Bogra, Pabna | Multiple Centers |
| **Khulna** | Khulna, Jessore, Satkhira | Multiple Centers |
| **Barisal** | Barisal, Patuakhali | Service Centers |
| **Sylhet** | Sylhet, Moulvibazar | Service Centers |
| **Rangpur** | Rangpur, Dinajpur | Service Centers |
| **Mymensingh** | Mymensingh, Jamalpur | Service Centers |

---

## 3. PROJECT SCOPE & OBJECTIVES

### 3.1 Business Objectives

The ERP implementation aims to achieve the following strategic business objectives:

**BO-1: Operational Unification**
Consolidate all business operations across 51+ service centers into a single, unified platform eliminating data silos and disconnected processes.

**BO-2: Process Automation**
Automate at least 70% of repetitive operational processes including service order routing, technician dispatch, inventory replenishment, invoicing, and reporting.

**BO-3: Real-Time Visibility**
Provide real-time dashboards and visibility into all operational KPIs across every service center, technician, and business function.

**BO-4: Customer Experience Excellence**
Enable seamless, omni-channel customer experience with self-service portals, real-time tracking, automated notifications, and faster service turnaround.

**BO-5: Financial Control & Compliance**
Implement robust financial controls with multi-branch accounting, automated VAT/tax compliance, warranty billing to brand partners, and consolidated financial reporting.

**BO-6: Workforce Optimization**
Optimize technician productivity through AI-powered dispatch, route optimization, skill-based assignment, and mobile-first field operations.

**BO-7: Inventory Optimization**
Achieve 98%+ inventory accuracy across all locations with automated replenishment, inter-branch transfers, and real-time stock visibility.

**BO-8: Scalable Growth**
Build a platform that scales to support 5x business growth over 5 years, including new service categories, geographic expansion, and 250,000+ monthly users.

**BO-9: Data-Driven Decision Making**
Establish a comprehensive BI and analytics capability with predictive insights, trend analysis, and executive dashboards.

**BO-10: Brand Partner Integration**
Streamline warranty claim processing and service reporting with all 17+ authorized brand partners.

### 3.2 Departments & Functions In Scope

| # | Department / Function | Priority | Key Processes |
|---|---|---|---|
| 1 | Service Operations | Critical | Service order lifecycle, dispatch, quality control |
| 2 | Field Service | Critical | Technician management, mobile operations, scheduling |
| 3 | Inventory & Warehouse | Critical | Multi-location stock, spare parts, transfers |
| 4 | Finance & Accounting | Critical | Billing, collections, GL, AP/AR, tax |
| 5 | CRM & Customer Service | Critical | Customer management, loyalty, communications |
| 6 | Contract Management | High | AMC, RAMC, warranty, SLAs |
| 7 | HR & Payroll | High | Employee lifecycle, payroll, training |
| 8 | Procurement | High | Vendor management, PO, spare parts sourcing |
| 9 | Sales & Marketing | High | Corporate sales, campaigns, lead management |
| 10 | Quality Management | Medium | ISO compliance, audits, CAPA |
| 11 | IT Administration | Medium | System admin, user management, security |
| 12 | Executive Management | Medium | Dashboards, approvals, strategic planning |

### 3.3 User Count Estimates

| User Category | Estimated Count | Access Type |
|---|---|---|
| Admin / Back-Office Users | 100-150 | Full ERP Desktop/Web |
| Field Technicians | 200-400 | Mobile App (PWA/Native) |
| Service Center Staff | 150-250 | ERP Desktop/Web |
| Customer Service Agents | 30-50 | CRM Module |
| Management / Executives | 15-25 | Dashboards & Reports |
| External Customers (Portal) | 50,000-250,000/month | Customer Portal |
| Corporate B2B Users (Portal) | 500-2,000 | B2B Portal |
| Vendor / Partners (Portal) | 100-500 | Vendor Portal |
| **Total Internal Users** | **500-900** | |
| **Total Portal Users** | **50,000-250,000+** | |

### 3.4 Integration with Existing Digital Platform

1000FiX is concurrently developing an 8-portal smart web platform using the following technology stack:

| Component | Technology |
|---|---|
| Frontend Framework | Next.js 15 |
| UI Framework | React 19, Tailwind CSS, shadcn/ui |
| CMS | Payload CMS 3.x |
| Database | PostgreSQL 16 with TimescaleDB |
| Cache | Redis 7 |
| ORM | Drizzle ORM |
| Real-time | Socket.io |
| AI/Chatbot | Rasa 3.6 (Bengali NLP) |
| Optimization | Timefold (route dispatch) |
| Queue | BullMQ |
| Hosting | Vercel + DigitalOcean + Cloudflare |

The ERP system must integrate seamlessly with this platform through well-documented APIs, webhooks, and shared data models. The web platform handles customer-facing interactions while the ERP manages back-office operations, and both must share real-time data.

---

## 4. CURRENT IT LANDSCAPE & PAIN POINTS

### 4.1 Current Systems

| System | Description | Limitations |
|---|---|---|
| WordPress Website | Current public website | Slow (5-7s load), limited functionality, poor mobile experience |
| Manual Service Tracking | Spreadsheets, phone calls, paper-based | No real-time visibility, error-prone, not scalable |
| Basic Accounting Software | Stand-alone financial management | No integration with operations, manual data entry |
| Phone-Based Dispatch | Manual technician assignment via calls | No optimization, no tracking, no performance data |
| Fragmented Inventory | Location-by-location tracking | No centralized visibility, stockouts, excess inventory |
| Manual Warranty Claims | Paper/email-based brand partner claims | Slow processing, revenue leakage, no tracking |
| No CRM | Customer data in multiple spreadsheets | No 360-degree customer view, no service history |
| Manual HR | Spreadsheet-based HR management | No automated payroll, attendance, or training tracking |

### 4.2 Key Pain Points

| # | Pain Point | Business Impact |
|---|---|---|
| 1 | **No Unified System** | Data silos across departments; decisions based on incomplete information |
| 2 | **Manual Service Order Processing** | Slow turnaround, errors, customer dissatisfaction |
| 3 | **Inefficient Technician Dispatch** | Low productivity (4-5 jobs/day), no route optimization |
| 4 | **Poor Inventory Visibility** | Stockouts at one location while excess at another; lost revenue |
| 5 | **Delayed Warranty Billing** | Revenue leakage from slow/missed warranty claims to brand partners |
| 6 | **No Real-Time Tracking** | Customers and management cannot track service status |
| 7 | **Manual Financial Processes** | 15-20 day month-end close, reconciliation errors |
| 8 | **No Performance Analytics** | Cannot measure technician productivity, service quality, or branch performance |
| 9 | **Scalability Constraints** | Current processes cannot support growth beyond current volume |
| 10 | **Customer Retention Risk** | No loyalty program management, no proactive engagement |

---

## 5. FUNCTIONAL REQUIREMENTS

Vendors must respond to each requirement with one of the following:

- **S** — Supported out of the box (standard feature)
- **C** — Supported with configuration (no custom code)
- **D** — Requires custom development
- **T** — Supported via third-party integration
- **N** — Not supported

Priority levels: **P1** = Must-Have, **P2** = Important, **P3** = Nice-to-Have

---

### 5.1 Service & Repair Management

This is the **core module** of the ERP system — the primary revenue-generating function of 1000FiX.

#### 5.1.1 Service Order Management

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| SRM-001 | Create service orders from multiple channels (phone, web portal, walk-in, WhatsApp, chatbot, email) | P1 | |
| SRM-002 | Classify service orders by type: Warranty, Out-of-Warranty, AMC/RAMC, Emergency, Preventive Maintenance | P1 | |
| SRM-003 | Support full service order lifecycle: Created → Assigned → In Progress → Parts Pending → Completed → Invoiced → Closed | P1 | |
| SRM-004 | Auto-assign unique service order number with configurable numbering scheme per branch | P1 | |
| SRM-005 | Link service orders to specific customer devices with serial number tracking | P1 | |
| SRM-006 | Capture device information: brand, model, serial number, purchase date, warranty status | P1 | |
| SRM-007 | Maintain complete service history per device (all past repairs, parts replaced, costs) | P1 | |
| SRM-008 | Support multiple service items per order (e.g., laptop repair + data recovery) | P1 | |
| SRM-009 | Define and track SLA timelines per service type, brand, and customer tier | P1 | |
| SRM-010 | SLA breach alerts with configurable escalation rules (email, SMS, dashboard notification) | P1 | |
| SRM-011 | Configurable service order statuses and sub-statuses per workflow | P2 | |
| SRM-012 | Internal notes and communication thread within each service order | P1 | |
| SRM-013 | Photo/video attachment capability for device condition documentation (before/after repair) | P1 | |
| SRM-014 | Automatic customer notifications at each status change (SMS, email, push notification) | P1 | |
| SRM-015 | Service order prioritization rules (VIP customers, emergency, SLA proximity) | P2 | |
| SRM-016 | Service order templates for common repair types per device category | P2 | |
| SRM-017 | Duplicate service order detection (same device, same issue within defined timeframe) | P2 | |
| SRM-018 | Service order splitting (splitting a single order into multiple sub-orders for different technicians) | P3 | |
| SRM-019 | Service order merging (combining related orders for the same customer) | P3 | |
| SRM-020 | Configurable approval workflows for high-value repairs or warranty claims | P1 | |

#### 5.1.2 Repair Workflow Management

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| SRM-021 | Multi-level repair classification: Level 1 (Basic), Level 2 (Intermediate), Level 3 (Advanced/Board-Level) | P1 | |
| SRM-022 | Diagnostic checklist templates per device type and issue category | P1 | |
| SRM-023 | Repair cost estimation with customer approval workflow before proceeding | P1 | |
| SRM-024 | Parts requisition from service order directly linked to inventory | P1 | |
| SRM-025 | Labor time tracking per service order and per technician | P1 | |
| SRM-026 | Quality inspection checklist upon repair completion | P1 | |
| SRM-027 | Post-repair testing and certification workflow | P2 | |
| SRM-028 | Warranty claim generation for warranty repairs linked to brand partner | P1 | |
| SRM-029 | Rework tracking — flag and track devices returned for the same issue | P1 | |
| SRM-030 | Root cause analysis categorization per repair | P2 | |

#### 5.1.3 Service Pricing & Estimation

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| SRM-031 | Configurable service price list by device category, brand, model, and repair type | P1 | |
| SRM-032 | Separate pricing for warranty vs. out-of-warranty services | P1 | |
| SRM-033 | Dynamic cost estimation (labor + parts + transport + taxes) | P1 | |
| SRM-034 | Customer-facing quotation generation with approval workflow | P1 | |
| SRM-035 | Discount management (privilege member discounts, promotional, bulk) | P1 | |
| SRM-036 | Not-to-Exceed (NTE) limits for corporate/B2B accounts with automatic approval routing | P2 | |
| SRM-037 | Price revision history and effective date management | P2 | |

---

### 5.2 Field Service Management

#### 5.2.1 Technician Scheduling & Dispatch

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| FSM-001 | AI-powered smart scheduling engine considering: technician skills, certifications, location, availability, workload, and priority | P1 | |
| FSM-002 | Drag-and-drop dispatch board with calendar view (daily, weekly, monthly) | P1 | |
| FSM-003 | Real-time GPS tracking of all field technicians | P1 | |
| FSM-004 | Route optimization for multiple jobs per technician per day (minimizing travel time and distance) | P1 | |
| FSM-005 | Skill-based assignment matching (e.g., AC technician vs. laptop technician vs. Apple specialist) | P1 | |
| FSM-006 | Emergency job insertion with automatic re-optimization of existing schedules | P1 | |
| FSM-007 | Automatic rescheduling suggestions when technician is running late or unavailable | P2 | |
| FSM-008 | Service territory/zone management with geo-fencing | P2 | |
| FSM-009 | Capacity planning — maximum jobs per technician per day with configurable limits | P1 | |
| FSM-010 | Travel time estimation between job sites using real-time traffic data | P2 | |
| FSM-011 | Preferred technician assignment for repeat customers | P3 | |
| FSM-012 | Batch scheduling for recurring maintenance (AMC/RAMC visits) | P2 | |

#### 5.2.2 Mobile Field Operations

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| FSM-013 | Mobile app (PWA or native iOS/Android) for field technicians | P1 | |
| FSM-014 | Offline mode with automatic data sync when connectivity is restored | P1 | |
| FSM-015 | Mobile job queue showing upcoming, current, and completed jobs | P1 | |
| FSM-016 | GPS navigation to job site (integrated with Google Maps) | P1 | |
| FSM-017 | Digital service forms and checklists on mobile | P1 | |
| FSM-018 | Before/after photo capture with timestamp and GPS location tags | P1 | |
| FSM-019 | Customer electronic signature capture on mobile device | P1 | |
| FSM-020 | Real-time status updates from field (en route, arrived, working, completed) | P1 | |
| FSM-021 | Parts consumption recording from mobile (scan barcode/QR code) | P1 | |
| FSM-022 | Time tracking (travel time, on-site time, repair time) with auto-capture | P1 | |
| FSM-023 | In-app messaging between technician and dispatch/customer | P2 | |
| FSM-024 | Knowledge base access from mobile (repair manuals, troubleshooting guides) | P2 | |
| FSM-025 | Expense reporting and reimbursement claims from mobile | P3 | |
| FSM-026 | Push notifications for new assignments, schedule changes, and alerts | P1 | |

#### 5.2.3 Service Delivery Tracking

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| FSM-027 | Real-time customer-facing tracking page showing technician location and ETA | P1 | |
| FSM-028 | Automatic SMS/notification when technician is dispatched, en route, and arriving | P1 | |
| FSM-029 | Pick & Drop service tracking — pickup scheduled, picked up, in repair, repair complete, delivery scheduled, delivered | P1 | |
| FSM-030 | Service center walk-in queue management with estimated wait times | P2 | |
| FSM-031 | Remote support session initiation and tracking | P3 | |

---

### 5.3 Inventory & Spare Parts Management

#### 5.3.1 Multi-Location Inventory

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| INV-001 | Multi-warehouse inventory management across 51+ service center locations | P1 | |
| INV-002 | Central warehouse and regional hub inventory management | P1 | |
| INV-003 | Technician van/mobile stock management (parts carried by field technicians) | P1 | |
| INV-004 | Real-time stock visibility across all locations from a single dashboard | P1 | |
| INV-005 | Unique item identification: barcode and QR code support | P1 | |
| INV-006 | Serial number tracking for high-value spare parts | P1 | |
| INV-007 | Batch/lot tracking for consumables | P2 | |
| INV-008 | Multi-unit of measure support (individual, pack, box, pallet) | P2 | |

#### 5.3.2 Stock Operations

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| INV-009 | Goods receipt (inbound) from purchase orders with quality inspection | P1 | |
| INV-010 | Inter-branch stock transfer with approval workflow and tracking | P1 | |
| INV-011 | Stock requisition from service orders with automatic reservation | P1 | |
| INV-012 | Automatic replenishment based on reorder points and consumption patterns | P1 | |
| INV-013 | Cycle counting and physical inventory reconciliation | P1 | |
| INV-014 | Dead stock identification and disposal workflow | P2 | |
| INV-015 | Warranty returns management (defective parts return to brand/supplier) | P1 | |
| INV-016 | Consignment inventory management (brand-owned stock held at 1000FiX locations) | P2 | |
| INV-017 | Stock valuation methods: FIFO, weighted average | P1 | |
| INV-018 | Minimum/maximum stock level alerts per item per location | P1 | |

#### 5.3.3 Parts Catalog

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| INV-019 | Master parts catalog with cross-reference to compatible device brands/models | P1 | |
| INV-020 | Genuine vs. compatible/aftermarket parts classification | P1 | |
| INV-021 | Parts pricing tiers: warranty (brand-reimbursed), out-of-warranty (customer-paid), internal | P1 | |
| INV-022 | Parts substitution/alternative parts mapping | P2 | |
| INV-023 | Parts image library | P3 | |
| INV-024 | Supplier lead time tracking per part | P2 | |

---

### 5.4 Customer Relationship Management (CRM)

#### 5.4.1 Customer Management

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| CRM-001 | 360-degree customer profile: contact info, devices, service history, payments, communications | P1 | |
| CRM-002 | Device registry per customer: brand, model, serial number, purchase date, warranty expiry | P1 | |
| CRM-003 | Customer segmentation: individual, corporate, privilege member, AMC holder | P1 | |
| CRM-004 | Customer communication history across all channels (phone, email, SMS, WhatsApp, portal) | P1 | |
| CRM-005 | Automated customer lifecycle communications (welcome, post-service follow-up, warranty reminders, birthday/anniversary) | P2 | |
| CRM-006 | Customer satisfaction surveys (automated post-service CSAT and NPS) | P1 | |
| CRM-007 | Customer feedback and complaint management with escalation workflows | P1 | |
| CRM-008 | Duplicate customer detection and merge functionality | P2 | |

#### 5.4.2 Loyalty & Membership Programs

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| CRM-009 | Privilege Program management — Silver, Gold, Diamond tiers with tier-based discounts | P1 | |
| CRM-010 | Membership enrollment, renewal, and upgrade workflows | P1 | |
| CRM-011 | Points/rewards system with earning and redemption rules | P2 | |
| CRM-012 | Promotional campaign management with coupon/voucher codes | P2 | |
| CRM-013 | Referral program tracking | P3 | |

#### 5.4.3 Sales & Lead Management

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| CRM-014 | Lead capture from website, phone, walk-in, corporate outreach | P2 | |
| CRM-015 | Corporate account management with multi-contact, multi-location support | P1 | |
| CRM-016 | Sales pipeline for corporate/B2B deals (AMC contracts, bulk service agreements) | P2 | |
| CRM-017 | Quotation generation for corporate clients with approval workflow | P1 | |
| CRM-018 | Sales forecast and revenue projection | P3 | |

---

### 5.5 Financial Management & Accounting

#### 5.5.1 General Ledger & Core Accounting

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| FIN-001 | Multi-branch chart of accounts with configurable account structure | P1 | |
| FIN-002 | Multi-cost center/profit center accounting (per branch, per service type, per brand) | P1 | |
| FIN-003 | General ledger with drill-down to transaction level | P1 | |
| FIN-004 | Journal entries — manual and automated from sub-ledgers | P1 | |
| FIN-005 | Bank reconciliation (manual and automated) | P1 | |
| FIN-006 | Multi-currency support (BDT primary, USD for international transactions) | P2 | |
| FIN-007 | Fixed asset management and depreciation | P2 | |
| FIN-008 | Period-end closing with automated checks and balances | P1 | |
| FIN-009 | Financial year and period configuration (Bangladesh fiscal year: July-June) | P1 | |

#### 5.5.2 Accounts Receivable

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| FIN-010 | Invoice generation from completed service orders (automatic) | P1 | |
| FIN-011 | Warranty claim invoicing to brand partners with required documentation | P1 | |
| FIN-012 | Corporate account invoicing with configurable billing cycles (weekly, bi-weekly, monthly) | P1 | |
| FIN-013 | AMC/RAMC subscription invoicing with automatic renewal billing | P1 | |
| FIN-014 | Multiple payment method recording: cash, card, bKash, Nagad, SSLCOMMERZ, bank transfer | P1 | |
| FIN-015 | Advance payment/deposit management | P2 | |
| FIN-016 | Credit note and refund management | P1 | |
| FIN-017 | Customer aging analysis and automated payment reminders | P1 | |
| FIN-018 | Collection management with follow-up workflow | P2 | |

#### 5.5.3 Accounts Payable

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| FIN-019 | Vendor invoice processing with 3-way matching (PO, receipt, invoice) | P1 | |
| FIN-020 | Payment scheduling and batch processing | P1 | |
| FIN-021 | Technician expense reimbursement processing | P2 | |
| FIN-022 | Vendor aging analysis | P1 | |
| FIN-023 | Automated payment approval workflows based on amount thresholds | P1 | |

#### 5.5.4 Tax & Compliance

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| FIN-024 | Bangladesh VAT (Value Added Tax) calculation and compliance | P1 | |
| FIN-025 | Tax withholding at source (TDS) as per Bangladesh tax laws | P1 | |
| FIN-026 | Automated VAT return preparation (Mushak forms) | P1 | |
| FIN-027 | Tax invoice generation per NBR (National Board of Revenue) requirements | P1 | |
| FIN-028 | Audit trail for all financial transactions | P1 | |

#### 5.5.5 Financial Reporting

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| FIN-029 | Balance sheet, profit & loss, cash flow statement (Bangladesh GAAP / IFRS) | P1 | |
| FIN-030 | Branch-wise P&L and consolidated financial statements | P1 | |
| FIN-031 | Revenue analysis by: service type, brand, device category, branch, customer segment | P1 | |
| FIN-032 | Cost analysis: labor cost, parts cost, overhead per service order | P1 | |
| FIN-033 | Budget vs. actual reporting with variance analysis | P2 | |
| FIN-034 | Warranty revenue tracking and reconciliation with brand partners | P1 | |
| FIN-035 | Configurable financial dashboards and custom report builder | P1 | |

---

### 5.6 Human Resource Management & Payroll

#### 5.6.1 Employee Management

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| HRM-001 | Employee master data: personal info, employment details, qualifications, emergency contacts | P1 | |
| HRM-002 | Employee lifecycle management: recruitment → onboarding → active → offboarding | P1 | |
| HRM-003 | Organization hierarchy and reporting structure | P1 | |
| HRM-004 | Employee document management (contracts, certificates, ID copies) | P2 | |
| HRM-005 | Employee self-service portal (leave requests, payslips, tax certificates) | P2 | |

#### 5.6.2 Technician Workforce Management

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| HRM-006 | Technician skill matrix: certifications, brand authorizations, specializations | P1 | |
| HRM-007 | Certification tracking with expiry alerts (e.g., Dell certified, HP authorized) | P1 | |
| HRM-008 | Training management: course catalog, enrollment, completion tracking, certification | P1 | |
| HRM-009 | Technician performance metrics: jobs completed, first-time fix rate, customer ratings, rework rate | P1 | |
| HRM-010 | Technician ranking and leaderboard | P2 | |
| HRM-011 | Shift management and roster planning for service center and field staff | P1 | |

#### 5.6.3 Attendance & Leave

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| HRM-012 | Attendance tracking with biometric/mobile clock-in integration | P1 | |
| HRM-013 | GPS-based attendance for field technicians (auto clock-in at first job site) | P2 | |
| HRM-014 | Leave management: types (annual, sick, casual, maternity/paternity), accruals, balances | P1 | |
| HRM-015 | Bangladesh public holiday calendar management | P1 | |
| HRM-016 | Overtime tracking and approval | P1 | |

#### 5.6.4 Payroll

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| HRM-017 | Payroll processing for monthly and contractual employees | P1 | |
| HRM-018 | Salary structure: basic, house rent, medical, transport, technical allowances | P1 | |
| HRM-019 | Incentive/commission calculation based on technician performance metrics | P1 | |
| HRM-020 | Statutory deductions: income tax (as per Bangladesh tax slabs), provident fund | P1 | |
| HRM-021 | Bank salary transfer file generation (for Bangladesh banks) | P1 | |
| HRM-022 | Payslip generation and distribution (email/portal) | P1 | |
| HRM-023 | Annual tax certificate generation (as per NBR requirements) | P2 | |

---

### 5.7 Contract & Warranty Management

#### 5.7.1 Annual Maintenance Contracts (AMC)

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| CWM-001 | AMC creation with configurable terms: coverage scope, response SLA, visits included, duration | P1 | |
| CWM-002 | RAMC (Residential Annual Maintenance Contract) management — 6 package types | P1 | |
| CWM-003 | Corporate AMC management with multi-location, multi-device coverage | P1 | |
| CWM-004 | Contract lifecycle: draft → approved → active → renewed/expired | P1 | |
| CWM-005 | Automatic scheduled maintenance visit generation from AMC terms | P1 | |
| CWM-006 | Contract utilization tracking (visits used vs. included) | P1 | |
| CWM-007 | Renewal alerts and automated renewal quotation generation (60/30/15 days before expiry) | P1 | |
| CWM-008 | Contract profitability analysis (revenue vs. cost of services delivered) | P2 | |

#### 5.7.2 Warranty Management

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| CWM-009 | Device warranty registration and tracking (manufacturer warranty + extended warranty) | P1 | |
| CWM-010 | Automated warranty status verification at service order creation (based on serial number + purchase date) | P1 | |
| CWM-011 | Warranty claim creation and submission to brand partners | P1 | |
| CWM-012 | Warranty claim lifecycle tracking: submitted → approved → parts shipped → completed → billed → paid | P1 | |
| CWM-013 | Warranty claim documentation management (photos, diagnostic reports, replaced parts) | P1 | |
| CWM-014 | Warranty revenue reconciliation with brand partner payments | P1 | |
| CWM-015 | Extended warranty program enrollment and management | P1 | |
| CWM-016 | Warranty extension pricing and billing | P1 | |
| CWM-017 | Brand-specific warranty terms and conditions configuration | P2 | |

#### 5.7.3 SLA Management

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| CWM-018 | SLA definition per service type, customer tier, contract type, and brand | P1 | |
| CWM-019 | SLA metrics: response time, resolution time, first-time fix rate, uptime | P1 | |
| CWM-020 | Real-time SLA monitoring dashboard with breach alerts | P1 | |
| CWM-021 | SLA escalation matrix with automatic escalation at configurable thresholds (50%, 75%, 90%, 100%) | P1 | |
| CWM-022 | SLA compliance reporting per branch, technician, brand, and contract | P1 | |

---

### 5.8 Procurement & Supply Chain Management

#### 5.8.1 Vendor Management

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| SCM-001 | Vendor master database with classification: OEM, authorized distributor, local supplier | P1 | |
| SCM-002 | Vendor qualification and onboarding workflow | P2 | |
| SCM-003 | Vendor performance scorecard: delivery time, quality, pricing, responsiveness | P1 | |
| SCM-004 | Vendor contract management with terms, pricing agreements, and renewal tracking | P1 | |
| SCM-005 | Vendor document management (trade license, TIN, VAT registration, insurance) | P2 | |

#### 5.8.2 Purchase Management

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| SCM-006 | Purchase requisition with approval workflow (branch-level and central) | P1 | |
| SCM-007 | Purchase order creation and management | P1 | |
| SCM-008 | Automatic PO generation from reorder point alerts | P2 | |
| SCM-009 | Purchase price comparison and best-price selection | P2 | |
| SCM-010 | Goods receipt and quality inspection | P1 | |
| SCM-011 | 3-way matching: PO → Goods Receipt → Vendor Invoice | P1 | |
| SCM-012 | Return to vendor (RTV) management for defective parts | P1 | |

---

### 5.9 Reporting & Business Intelligence

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| BI-001 | Executive dashboard with real-time KPIs: revenue, orders, SLA compliance, customer satisfaction | P1 | |
| BI-002 | Branch performance dashboard: orders, revenue, cost, profitability, technician utilization per location | P1 | |
| BI-003 | Technician performance analytics: jobs completed, productivity, first-time fix rate, customer ratings, earnings | P1 | |
| BI-004 | Service analytics: turnaround time, most common issues, rework rate, parts consumption | P1 | |
| BI-005 | Inventory analytics: stock levels, turnover, dead stock, inter-branch movement | P1 | |
| BI-006 | Financial analytics: revenue trends, cost analysis, profitability by service/brand/branch | P1 | |
| BI-007 | Customer analytics: acquisition, retention, lifetime value, satisfaction trends | P2 | |
| BI-008 | Warranty analytics: claims by brand, approval rates, revenue realization, aging | P1 | |
| BI-009 | Custom report builder with drag-and-drop interface | P1 | |
| BI-010 | Scheduled report generation and email distribution | P1 | |
| BI-011 | Data export in multiple formats: PDF, Excel, CSV | P1 | |
| BI-012 | Ad-hoc query capability for power users | P2 | |
| BI-013 | Predictive analytics: demand forecasting, seasonal trends, resource planning | P3 | |
| BI-014 | Integration with Metabase or equivalent BI tool for advanced analytics | P2 | |

---

### 5.10 Document Management System

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| DMS-001 | Centralized document storage with version control | P1 | |
| DMS-002 | Document categorization: service reports, invoices, contracts, warranty claims, compliance | P1 | |
| DMS-003 | Digital form builder for custom forms and checklists | P2 | |
| DMS-004 | Electronic signature capture and verification | P1 | |
| DMS-005 | Document approval workflows with audit trail | P1 | |
| DMS-006 | Document templates: service reports, quotations, invoices, certificates | P1 | |
| DMS-007 | Bulk document scanning and OCR capability | P3 | |
| DMS-008 | Document retention policies and automated archiving | P2 | |

---

### 5.11 Quality Management System

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| QMS-001 | ISO 9001:2015 compliance tracking and documentation | P1 | |
| QMS-002 | Internal audit management with audit plans, findings, and corrective actions | P2 | |
| QMS-003 | Non-conformance report (NCR) management | P2 | |
| QMS-004 | Corrective and Preventive Action (CAPA) tracking | P2 | |
| QMS-005 | Customer complaint management with root cause analysis | P1 | |
| QMS-006 | Service quality scoring per technician, branch, and service type | P1 | |
| QMS-007 | Standard operating procedure (SOP) management and version control | P2 | |
| QMS-008 | Quality KPI dashboards: rework rate, customer complaints, SLA compliance, CSAT scores | P1 | |

---

## 6. SMART PORTAL SUITE REQUIREMENTS

The ERP system must include or integrate with the following smart portal suite, providing role-based access to various stakeholders.

---

### 6.1 Customer Self-Service Portal

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| CSP-001 | Customer registration and login (email, phone, social media) | P1 | |
| CSP-002 | Service request submission wizard (device type → issue → schedule → payment) | P1 | |
| CSP-003 | Real-time service order tracking with technician location and ETA | P1 | |
| CSP-004 | Service history and device registry view | P1 | |
| CSP-005 | Invoice and payment history | P1 | |
| CSP-006 | Online payment (bKash, Nagad, SSLCOMMERZ, card) | P1 | |
| CSP-007 | Appointment scheduling and rescheduling | P1 | |
| CSP-008 | Customer feedback and rating submission | P1 | |
| CSP-009 | Privilege program membership management (view tier, benefits, renewal) | P1 | |
| CSP-010 | Warranty extension purchase and management | P2 | |
| CSP-011 | AMC/RAMC subscription management | P2 | |
| CSP-012 | Knowledge base and FAQ access | P2 | |
| CSP-013 | Live chat integration (AI chatbot + human agent escalation) | P2 | |
| CSP-014 | Push notifications and communication preferences | P1 | |
| CSP-015 | Multi-language support: Bengali and English | P1 | |
| CSP-016 | Responsive design and PWA capability for mobile | P1 | |
| CSP-017 | Multi-address management with map selection | P1 | |

---

### 6.2 Technician Mobile Portal

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| TMP-001 | Mobile-first design optimized for smartphone use in field conditions | P1 | |
| TMP-002 | Daily job queue with priority, schedule, and navigation | P1 | |
| TMP-003 | Job acceptance/rejection with reason logging | P1 | |
| TMP-004 | One-tap GPS navigation to customer location | P1 | |
| TMP-005 | Digital service forms with pre-populated device/customer data | P1 | |
| TMP-006 | Photo/video capture for device condition documentation | P1 | |
| TMP-007 | Parts consumption recording with barcode scanning | P1 | |
| TMP-008 | Time tracking (auto-capture travel, on-site, and repair time) | P1 | |
| TMP-009 | Customer e-signature capture for service completion | P1 | |
| TMP-010 | Offline mode with automatic sync on reconnect | P1 | |
| TMP-011 | Earnings dashboard: daily/weekly/monthly performance and incentives | P2 | |
| TMP-012 | Knowledge base: repair manuals, troubleshooting guides, training materials | P2 | |
| TMP-013 | In-app communication with dispatch and customer | P2 | |
| TMP-014 | Leave request and schedule management | P2 | |
| TMP-015 | Parts request for items not in van stock | P1 | |
| TMP-016 | Push notifications for new jobs, changes, and alerts | P1 | |
| TMP-017 | Multi-language support: Bengali and English | P1 | |

---

### 6.3 Admin Operations Portal

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| AOP-001 | Real-time operational dashboard: live service orders, technician locations, SLA status | P1 | |
| AOP-002 | Service order management: create, edit, assign, reassign, escalate, cancel | P1 | |
| AOP-003 | Dispatch control center with drag-and-drop scheduling | P1 | |
| AOP-004 | Live technician tracking map with status indicators | P1 | |
| AOP-005 | Customer management: search, view profiles, manage accounts | P1 | |
| AOP-006 | Inventory management: stock levels, transfers, adjustments | P1 | |
| AOP-007 | Financial overview: daily collections, outstanding invoices, warranty claims | P1 | |
| AOP-008 | Notification center with configurable alerts and escalations | P1 | |
| AOP-009 | System configuration: service catalog, pricing, SLAs, workflows | P1 | |
| AOP-010 | User and role management with granular permissions | P1 | |
| AOP-011 | Bulk operations: mass assignment, status updates, notifications | P2 | |
| AOP-012 | Audit log viewer | P1 | |

---

### 6.4 Corporate B2B Portal

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| B2B-001 | Corporate account dashboard: active contracts, service summary, invoices | P1 | |
| B2B-002 | Multi-location management for corporate clients | P1 | |
| B2B-003 | Bulk service request submission with CSV/Excel upload | P1 | |
| B2B-004 | AMC/contract management: view terms, utilization, renewal | P1 | |
| B2B-005 | Consolidated invoicing and payment management | P1 | |
| B2B-006 | Service analytics and reports per location, device type, and period | P1 | |
| B2B-007 | Authorized requester management (who can submit service requests) | P1 | |
| B2B-008 | NTE (Not-to-Exceed) limit management and approval workflows | P2 | |
| B2B-009 | SLA compliance dashboard | P1 | |
| B2B-010 | Dedicated account manager assignment and communication | P2 | |

---

### 6.5 Vendor & Partner Portal

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| VPP-001 | Vendor self-service registration and onboarding | P2 | |
| VPP-002 | Purchase order acknowledgment and delivery tracking | P1 | |
| VPP-003 | Invoice submission and payment tracking | P1 | |
| VPP-004 | Warranty claim status and documentation exchange | P1 | |
| VPP-005 | Parts catalog and pricing management | P2 | |
| VPP-006 | Performance scorecard visibility | P2 | |
| VPP-007 | Compliance document upload and management | P2 | |
| VPP-008 | Communication and collaboration tools | P3 | |

---

### 6.6 Analytics & Business Intelligence Dashboard

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| ABD-001 | Executive summary dashboard with configurable KPIs | P1 | |
| ABD-002 | Real-time operational metrics: orders today, technicians active, SLA status | P1 | |
| ABD-003 | Financial dashboards: revenue, cost, profitability, cash flow | P1 | |
| ABD-004 | Customer dashboards: acquisition, retention, satisfaction, lifetime value | P2 | |
| ABD-005 | Branch comparison dashboards with ranking | P1 | |
| ABD-006 | Trend analysis with historical data comparison | P1 | |
| ABD-007 | Drill-down capability from summary to transaction level | P1 | |
| ABD-008 | Custom dashboard builder for different user roles | P2 | |
| ABD-009 | Mobile-responsive dashboard access | P1 | |
| ABD-010 | Automated alert/notification when KPIs exceed thresholds | P1 | |

---

## 7. TECHNICAL REQUIREMENTS

### 7.1 Architecture & Infrastructure

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| TECH-001 | Cloud-native SaaS architecture (preferred) or cloud-hosted deployment | P1 | |
| TECH-002 | Multi-tenant architecture with data isolation per organization | P1 | |
| TECH-003 | Microservices or modular architecture enabling independent module deployment | P2 | |
| TECH-004 | Horizontal scalability to support growth from 500 to 5,000+ concurrent users | P1 | |
| TECH-005 | Auto-scaling capability for peak demand periods | P2 | |
| TECH-006 | High availability with 99.9% uptime SLA | P1 | |
| TECH-007 | Disaster recovery with RPO < 1 hour and RTO < 4 hours | P1 | |
| TECH-008 | Data centers in South/Southeast Asia region for low latency (Bangladesh users) | P1 | |
| TECH-009 | Load balancing across multiple application instances | P2 | |
| TECH-010 | Container-based deployment (Docker/Kubernetes) preferred | P3 | |

### 7.2 Performance Requirements

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| TECH-011 | Page load time: < 3 seconds for typical operations | P1 | |
| TECH-012 | API response time: < 500ms for 95th percentile | P1 | |
| TECH-013 | Report generation: < 30 seconds for standard reports | P1 | |
| TECH-014 | Support for 500+ concurrent internal users | P1 | |
| TECH-015 | Support for 50,000+ concurrent portal users | P1 | |
| TECH-016 | Batch processing capability for bulk operations (10,000+ records) | P2 | |
| TECH-017 | Real-time data synchronization across all modules (< 5 second delay) | P1 | |

### 7.3 Mobile & Accessibility

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| TECH-018 | Responsive web design for all portal interfaces | P1 | |
| TECH-019 | Native mobile app (iOS + Android) or PWA for technician portal | P1 | |
| TECH-020 | Offline mode with local data storage and auto-sync | P1 | |
| TECH-021 | Camera, GPS, and barcode scanner integration on mobile | P1 | |
| TECH-022 | Push notification support (mobile and web) | P1 | |
| TECH-023 | Low bandwidth optimization for field operations in rural Bangladesh | P1 | |
| TECH-024 | WCAG 2.1 AA accessibility compliance | P2 | |

### 7.4 Localization

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| TECH-025 | Full Bengali language support (UI, notifications, reports, data entry) | P1 | |
| TECH-026 | English language support as secondary language | P1 | |
| TECH-027 | User-level language preference switching | P1 | |
| TECH-028 | Bengali Unicode support for all text fields and reports | P1 | |
| TECH-029 | Bangladesh date format (DD/MM/YYYY) and number format support | P1 | |
| TECH-030 | BDT (Bangladeshi Taka) as primary currency | P1 | |
| TECH-031 | Bangladesh phone number format validation (+880) | P1 | |

### 7.5 Customization & Extensibility

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| TECH-032 | No-code/low-code configuration for workflows, forms, and business rules | P1 | |
| TECH-033 | Customizable dashboards and report builder | P1 | |
| TECH-034 | Custom field creation on standard entities without coding | P1 | |
| TECH-035 | Workflow automation engine with trigger-action rules | P1 | |
| TECH-036 | API-first architecture for custom integrations | P1 | |
| TECH-037 | Plugin/extension framework for custom module development | P2 | |
| TECH-038 | White-labeling capability (branding, logos, color schemes) | P2 | |

---

## 8. INTEGRATION REQUIREMENTS

### 8.1 Existing Platform Integration

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| INT-001 | RESTful API integration with 1000FiX web platform (Next.js 15 + Payload CMS 3) | P1 | |
| INT-002 | Shared customer and device data synchronization between ERP and web platform | P1 | |
| INT-003 | Service order creation from web platform automatically reflected in ERP | P1 | |
| INT-004 | Real-time booking availability sync between web platform and ERP scheduling engine | P1 | |
| INT-005 | Webhook support for event-driven integration (order created, status changed, payment received) | P1 | |
| INT-006 | Shared authentication (SSO) between ERP and web platform portals | P2 | |

### 8.2 Payment Gateway Integration

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| INT-007 | bKash payment gateway integration | P1 | |
| INT-008 | Nagad payment gateway integration | P1 | |
| INT-009 | SSLCOMMERZ payment gateway integration (card payments) | P1 | |
| INT-010 | Rocket mobile banking integration | P2 | |
| INT-011 | Payment reconciliation with ERP accounting module | P1 | |
| INT-012 | Refund processing through payment gateways | P1 | |

### 8.3 Communication Integration

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| INT-013 | SMS gateway integration for Bangladesh (automated service notifications) | P1 | |
| INT-014 | Email integration (transactional emails: order confirmations, invoices, reminders) | P1 | |
| INT-015 | WhatsApp Business API integration for customer communication | P1 | |
| INT-016 | Push notification service integration (Firebase/APNs) | P1 | |
| INT-017 | VoIP/telephony integration for call center operations | P3 | |

### 8.4 Mapping & Location Services

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| INT-018 | Google Maps API integration for address geocoding and technician tracking | P1 | |
| INT-019 | Route optimization engine integration (Google Routes API or Timefold) | P1 | |
| INT-020 | Real-time traffic data for travel time estimation | P2 | |
| INT-021 | Geo-fencing for service zone management | P2 | |

### 8.5 AI & Automation Integration

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| INT-022 | AI chatbot integration (Rasa 3.6 with Bengali NLP) for automated customer support | P2 | |
| INT-023 | AI-powered dispatch optimization engine | P2 | |
| INT-024 | Machine learning-based demand forecasting for inventory management | P3 | |
| INT-025 | Predictive maintenance recommendations based on device and service history | P3 | |

### 8.6 Other Integrations

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| INT-026 | Accounting software integration (if existing standalone accounting system to be maintained) | P2 | |
| INT-027 | HR/Payroll software integration (if existing standalone HR system to be maintained) | P2 | |
| INT-028 | Biometric device integration for attendance | P2 | |
| INT-029 | Barcode/QR code printer integration for inventory labels | P2 | |
| INT-030 | Cloud storage integration (Cloudinary or equivalent for document/image storage) | P1 | |
| INT-031 | Metabase or equivalent BI tool integration for advanced analytics | P2 | |

---

## 9. DATA MIGRATION REQUIREMENTS

### 9.1 Data Sources

| Data Source | Description | Estimated Volume | Priority |
|---|---|---|---|
| Customer Data | Existing customer records from spreadsheets, phone records, website registrations | 100,000+ records | P1 |
| Device Registry | Device information, serial numbers, warranty details | 200,000+ records | P1 |
| Service History | Past service orders and repair records | 500,000+ records | P1 |
| Financial Data | Accounting records, invoices, payments | 3+ years of history | P1 |
| Inventory Data | Current stock levels across all locations | 10,000+ SKUs | P1 |
| Employee Data | HR records, technician profiles, certifications | 500+ records | P1 |
| Vendor Data | Supplier and partner information | 200+ records | P1 |
| Contract Data | Active AMC, RAMC, corporate contracts | 5,000+ records | P1 |
| Document Archive | Service reports, warranty documents, photos | TBD (significant volume) | P2 |

### 9.2 Migration Requirements

| Req # | Requirement | Priority |
|---|---|---|
| MIG-001 | Detailed data migration plan with mapping from source to target | P1 |
| MIG-002 | Data cleansing and deduplication before migration | P1 |
| MIG-003 | Data validation rules and reconciliation reports | P1 |
| MIG-004 | Trial migration with user acceptance testing before go-live | P1 |
| MIG-005 | Rollback plan in case of migration failures | P1 |
| MIG-006 | Data migration tools and utilities provided by vendor | P1 |
| MIG-007 | Support for incremental/delta migration during parallel run period | P2 |
| MIG-008 | Historical data migration with full audit trail preservation | P1 |
| MIG-009 | Data conversion from Bangla text formats as needed | P2 |

---

## 10. SECURITY & COMPLIANCE REQUIREMENTS

### 10.1 Authentication & Access Control

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| SEC-001 | Role-Based Access Control (RBAC) with granular permissions at field level | P1 | |
| SEC-002 | Multi-Factor Authentication (MFA) for all users | P1 | |
| SEC-003 | Single Sign-On (SSO) support (SAML 2.0, OAuth 2.0, OpenID Connect) | P2 | |
| SEC-004 | Password policies: minimum length, complexity, expiry, history | P1 | |
| SEC-005 | Session management: timeout, concurrent session limits, forced logout | P1 | |
| SEC-006 | IP-based access restrictions for admin portals | P2 | |
| SEC-007 | Branch-level data access restrictions (users see only their branch data unless authorized) | P1 | |

### 10.2 Data Security

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| SEC-008 | AES-256 encryption for data at rest | P1 | |
| SEC-009 | TLS 1.2+ encryption for data in transit | P1 | |
| SEC-010 | Database encryption with key management | P1 | |
| SEC-011 | PII (Personally Identifiable Information) data masking for non-production environments | P1 | |
| SEC-012 | Data backup encryption | P1 | |
| SEC-013 | Secure file upload with malware scanning | P2 | |

### 10.3 Audit & Compliance

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| SEC-014 | Complete audit trail for all data changes (who, what, when, before/after values) | P1 | |
| SEC-015 | Audit log tamper protection (immutable logs) | P1 | |
| SEC-016 | ISO 27001 compliance or equivalent security certification | P1 | |
| SEC-017 | SOC 2 Type II compliance | P2 | |
| SEC-018 | Bangladesh ICT Act compliance | P1 | |
| SEC-019 | GDPR-compatible data privacy controls (for potential international operations) | P3 | |
| SEC-020 | Regular penetration testing reports (at least annually) | P1 | |
| SEC-021 | Vulnerability management and patching process | P1 | |
| SEC-022 | Data retention and deletion policies configurable by data type | P1 | |

---

## 11. IMPLEMENTATION APPROACH & TIMELINE

### 11.1 Preferred Implementation Methodology

1000FiX prefers an **Agile/Iterative** implementation approach with the following characteristics:

- Sprint-based delivery with 2-3 week sprint cycles
- Regular demos and user acceptance testing
- Phased go-live with progressive module rollout
- Continuous feedback incorporation

### 11.2 Proposed Phased Rollout

| Phase | Modules | Duration | Description |
|---|---|---|---|
| **Phase 1: Foundation** | Service & Repair, CRM, Basic Inventory | Months 1-4 | Core service operations to replace manual processes |
| **Phase 2: Field Operations** | Field Service, Technician Portal, Route Optimization | Months 4-7 | Mobile-first technician operations |
| **Phase 3: Financial Control** | Finance & Accounting, Invoicing, Payment Integration | Months 7-10 | Financial management and automation |
| **Phase 4: Contracts & Partners** | Contract/Warranty Management, Vendor Portal, B2B Portal | Months 10-13 | Partner ecosystem management |
| **Phase 5: Workforce & Intelligence** | HR & Payroll, BI/Analytics, Quality Management | Months 13-16 | Workforce optimization and business intelligence |
| **Phase 6: Optimization** | AI Dispatch, Advanced Analytics, Process Optimization | Months 16-18 | AI-powered optimization and refinement |

### 11.3 Timeline Expectations

| Milestone | Expected Timeline |
|---|---|
| Vendor selection and contract signing | Month 0 |
| Project kickoff and discovery | Month 1 |
| Phase 1 go-live | Month 4 |
| Phase 2 go-live | Month 7 |
| Phase 3 go-live | Month 10 |
| Phase 4 go-live | Month 13 |
| Phase 5 go-live | Month 16 |
| Full system go-live | Month 18 |
| Post-implementation stabilization | Months 18-21 |
| Project closure | Month 21 |

**Total estimated project duration: 18-21 months**

### 11.4 Vendor Deliverables per Phase

For each implementation phase, the vendor must deliver:

1. Detailed design document with 1000FiX approval
2. Configured/developed modules per approved design
3. Unit testing and integration testing results
4. User Acceptance Testing (UAT) support
5. Data migration for the phase
6. User training materials and sessions
7. Go-live support with on-site presence
8. Post-go-live stabilization support (minimum 30 days)
9. Updated documentation reflecting actual implementation

---

## 12. TRAINING & CHANGE MANAGEMENT

### 12.1 Training Requirements

| Req # | Requirement | Priority |
|---|---|---|
| TRN-001 | Role-based training programs for each user category | P1 |
| TRN-002 | Train-the-Trainer (ToT) program for 1000FiX internal champions | P1 |
| TRN-003 | Training in Bengali language for field staff and service center employees | P1 |
| TRN-004 | Hands-on training in sandbox/training environment | P1 |
| TRN-005 | Video-based training library for on-demand learning | P1 |
| TRN-006 | User manuals and quick reference guides (Bengali and English) | P1 |
| TRN-007 | In-application guided tours and contextual help | P2 |
| TRN-008 | Training effectiveness assessment (pre/post-training evaluation) | P2 |
| TRN-009 | Refresher training sessions post-go-live (quarterly for first year) | P2 |
| TRN-010 | Training for system administrators on configuration, customization, and maintenance | P1 |

### 12.2 Training Volumes

| User Group | Estimated Users | Training Duration | Format |
|---|---|---|---|
| Executive/Management | 15-25 | 1 day | In-person workshop |
| Service Operations | 30-50 | 3-5 days | Classroom + hands-on |
| Field Technicians | 200-400 | 2-3 days (per batch of 30) | Mobile-focused, hands-on |
| Service Center Staff | 150-250 | 3-5 days (per batch of 30) | Classroom + hands-on |
| Customer Service | 30-50 | 2-3 days | Classroom + hands-on |
| Finance | 15-25 | 3-5 days | Classroom + hands-on |
| HR | 10-15 | 2-3 days | Classroom + hands-on |
| System Administrators | 5-10 | 5-10 days | Technical deep-dive |

### 12.3 Change Management

| Req # | Requirement | Priority |
|---|---|---|
| CHM-001 | Change management strategy and communication plan | P1 |
| CHM-002 | Stakeholder impact assessment | P1 |
| CHM-003 | Executive sponsorship and champion identification program | P1 |
| CHM-004 | Regular communication updates throughout implementation | P1 |
| CHM-005 | User adoption metrics tracking and intervention plan | P2 |
| CHM-006 | Feedback collection mechanism during and after rollout | P1 |

---

## 13. SUPPORT & MAINTENANCE REQUIREMENTS

### 13.1 Post-Implementation Support

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| SUP-001 | Dedicated support team with Bangladesh business hours coverage (9 AM - 9 PM BST, Sun-Thu) | P1 | |
| SUP-002 | 24/7 critical issue support for system-down scenarios | P1 | |
| SUP-003 | Ticketing system for issue logging, tracking, and resolution | P1 | |
| SUP-004 | Service Level Agreements for issue resolution: Critical (4 hrs), High (8 hrs), Medium (24 hrs), Low (72 hrs) | P1 | |
| SUP-005 | Dedicated account manager for 1000FiX | P1 | |
| SUP-006 | Quarterly business reviews with improvement recommendations | P2 | |
| SUP-007 | On-site support availability when required | P2 | |
| SUP-008 | Bengali-speaking support staff availability | P1 | |

### 13.2 System Maintenance

| Req # | Requirement | Priority | Vendor Response |
|---|---|---|---|
| SUP-009 | Regular system updates and patches (minimum quarterly) | P1 | |
| SUP-010 | Security patches within 48 hours of critical vulnerability discovery | P1 | |
| SUP-011 | Zero-downtime deployment for updates | P2 | |
| SUP-012 | Planned maintenance windows communicated 72 hours in advance | P1 | |
| SUP-013 | Automated system health monitoring with proactive alerts | P1 | |
| SUP-014 | Regular database optimization and performance tuning | P1 | |
| SUP-015 | Backup verification and disaster recovery testing (minimum bi-annually) | P1 | |

### 13.3 Warranty & Guarantee

| Req # | Requirement | Priority |
|---|---|---|
| SUP-016 | Minimum 12-month post-go-live warranty for defect fixes at no additional cost | P1 |
| SUP-017 | Performance guarantee: system meets all agreed performance benchmarks during warranty | P1 |
| SUP-018 | Data integrity guarantee during migration and operations | P1 |
| SUP-019 | Escrow arrangement for source code (if proprietary solution) | P2 |

---

## 14. VENDOR QUALIFICATIONS & EXPERIENCE

### 14.1 Company Profile Requirements

Vendors must provide the following information:

| # | Requirement |
|---|---|
| VQ-001 | Company legal name, registration, and incorporation details |
| VQ-002 | Year established and years in ERP implementation business |
| VQ-003 | Company size: total employees, ERP consultants, developers, support staff |
| VQ-004 | Office locations (especially South Asia presence) |
| VQ-005 | Annual revenue for the last 3 fiscal years |
| VQ-006 | Financial stability documentation (audited financial statements or references) |
| VQ-007 | Quality certifications: ISO 9001, ISO 27001, CMMI, or equivalent |
| VQ-008 | Product name, version, and technology platform details |
| VQ-009 | Product roadmap for the next 3 years |

### 14.2 Relevant Experience

| # | Requirement |
|---|---|
| VQ-010 | Number of ERP implementations completed in the last 5 years |
| VQ-011 | Experience with field service management companies (minimum 3 references) |
| VQ-012 | Experience with multi-location service businesses (minimum 3 references) |
| VQ-013 | Experience in Bangladesh or South Asia region (highly preferred) |
| VQ-014 | Experience with service/repair industry (after-sales service, warranty management) |
| VQ-015 | Case studies of similar implementations with measurable business outcomes |
| VQ-016 | Bengali language and localization experience |

### 14.3 Team Requirements

| # | Requirement |
|---|---|
| VQ-017 | Proposed project manager with PMP/Prince2 certification and 10+ years experience |
| VQ-018 | Solution architect with 10+ years ERP experience |
| VQ-019 | Functional consultants with field service/repair industry domain expertise |
| VQ-020 | Technical consultants experienced in integration with modern web platforms (Next.js, PostgreSQL, REST APIs) |
| VQ-021 | Data migration specialist |
| VQ-022 | Change management specialist |
| VQ-023 | Bengali-speaking team members or local implementation partner |
| VQ-024 | Resumes/CVs of all proposed key team members |

### 14.4 References

| # | Requirement |
|---|---|
| VQ-025 | Minimum 3 client references from field service/repair industry |
| VQ-026 | Minimum 2 client references from South Asia region |
| VQ-027 | For each reference: company name, contact person, project scope, duration, outcome |
| VQ-028 | Permission for 1000FiX to contact references directly |

---

## 15. BUDGET & PRICING STRUCTURE

### 15.1 Budget Indication

The indicative budget range for this project is **USD $150,000 — $350,000** (Total Cost of Ownership for 3 years), depending on the solution architecture, licensing model, and implementation scope. Vendors are encouraged to propose solutions within this range, with clear justification for any costs exceeding this envelope.

### 15.2 Pricing Structure

Vendors must provide pricing in the following format:

#### 15.2.1 Software Licensing

| Item | One-Time Cost (USD) | Annual Recurring Cost (USD) | Basis (per user, flat, etc.) |
|---|---|---|---|
| ERP Core Platform License | | | |
| Service & Repair Module | | | |
| Field Service Module | | | |
| Inventory Module | | | |
| CRM Module | | | |
| Financial Management Module | | | |
| HR & Payroll Module | | | |
| Contract/Warranty Module | | | |
| Procurement Module | | | |
| BI & Reporting Module | | | |
| Document Management Module | | | |
| Quality Management Module | | | |
| Customer Portal | | | |
| Technician Mobile Portal | | | |
| Admin Portal | | | |
| B2B Portal | | | |
| Vendor Portal | | | |
| Analytics Dashboard | | | |
| **Total Licensing** | | | |

#### 15.2.2 Implementation Services

| Item | Estimated Cost (USD) | Basis |
|---|---|---|
| Project Management | | |
| Business Analysis & Design | | |
| System Configuration | | |
| Custom Development | | |
| Integration Development | | |
| Data Migration | | |
| Testing (SIT, UAT) | | |
| Go-Live Support | | |
| Post-Go-Live Stabilization | | |
| **Total Implementation** | | |

#### 15.2.3 Training

| Item | Estimated Cost (USD) | Basis |
|---|---|---|
| Train-the-Trainer Program | | |
| End-User Training | | |
| Administrator Training | | |
| Training Materials Development | | |
| Video Training Content | | |
| **Total Training** | | |

#### 15.2.4 Infrastructure & Hosting

| Item | Annual Cost (USD) | Basis |
|---|---|---|
| Cloud Hosting/SaaS Fee | | |
| Database Hosting | | |
| Storage (Data + Documents) | | |
| CDN/Network | | |
| SSL/Security Certificates | | |
| **Total Infrastructure** | | |

#### 15.2.5 Ongoing Support & Maintenance

| Item | Annual Cost (USD) | Basis |
|---|---|---|
| Annual Maintenance & Support (AMS) | | |
| Premium Support (24/7) | | |
| Enhancement Hours (pool) | | |
| **Total Support** | | |

#### 15.2.6 Total Cost of Ownership Summary

| Category | Year 1 (USD) | Year 2 (USD) | Year 3 (USD) | 3-Year Total (USD) |
|---|---|---|---|---|
| Licensing | | | | |
| Implementation | | | | |
| Training | | | | |
| Infrastructure | | | | |
| Support & Maintenance | | | | |
| **Grand Total** | | | | |

### 15.3 Payment Terms

Vendors should propose payment milestones tied to deliverables. 1000FiX prefers the following general structure:

- 10% — Contract signing
- 15% — Completion of design phase
- 20% — Phase 1 go-live acceptance
- 15% — Phase 2 go-live acceptance
- 15% — Phase 3 go-live acceptance
- 10% — Phase 4 go-live acceptance
- 10% — Phase 5 go-live acceptance
- 5% — Final acceptance and project closure

---

## 16. EVALUATION CRITERIA

### 16.1 Evaluation Process

The evaluation will follow a structured, multi-stage process:

1. **Stage 1 — Compliance Review** (Pass/Fail): Verify all mandatory submission requirements are met
2. **Stage 2 — Technical Evaluation** (Weighted Scoring): Detailed assessment by evaluation committee
3. **Stage 3 — Vendor Demonstration** (Scripted Demo): Live demonstration of key scenarios
4. **Stage 4 — Reference Checks**: Contact provided references
5. **Stage 5 — Commercial Evaluation**: Total cost of ownership analysis
6. **Stage 6 — Final Scoring & Negotiation**: Combined score and contract negotiation

### 16.2 Scoring Matrix

| # | Evaluation Criteria | Weight | Max Score |
|---|---|---|---|
| 1 | **Functional Fit — Core Modules** (Service/Repair, Field Service, Inventory) | 25% | 100 |
| 2 | **Functional Fit — Supporting Modules** (Finance, HR, CRM, Contracts, Procurement) | 15% | 100 |
| 3 | **Smart Portal Suite Capabilities** | 12% | 100 |
| 4 | **Technical Architecture & Performance** | 12% | 100 |
| 5 | **Integration Capabilities** (APIs, web platform, payment gateways) | 8% | 100 |
| 6 | **Mobile & Offline Capabilities** | 8% | 100 |
| 7 | **Vendor Experience & References** (field service industry, South Asia) | 7% | 100 |
| 8 | **Implementation Approach & Team** | 5% | 100 |
| 9 | **Total Cost of Ownership** (3-year) | 5% | 100 |
| 10 | **Support & Maintenance** | 3% | 100 |
| **Total** | | **100%** | |

### 16.3 Scoring Scale

| Score | Description |
|---|---|
| 90-100 | Excellent — Fully meets and significantly exceeds requirements |
| 70-89 | Good — Meets all requirements with minor gaps |
| 50-69 | Adequate — Meets most requirements but some gaps require attention |
| 30-49 | Below Average — Significant gaps; requires substantial customization |
| 0-29 | Poor — Does not meet requirements |

---

## 17. SUBMISSION GUIDELINES & INSTRUCTIONS

### 17.1 Key Dates

| Event | Date |
|---|---|
| RFP Issuance | March 17, 2026 |
| Vendor Questions Submission Deadline | April 7, 2026 |
| Answers to Vendor Questions Published | April 14, 2026 |
| Proposal Submission Deadline | **May 15, 2026, 5:00 PM BST** |
| Proposal Evaluation Period | May 16 — June 13, 2026 |
| Vendor Shortlisting Notification | June 16, 2026 |
| Vendor Demonstrations | June 23 — July 4, 2026 |
| Reference Checks | July 7 — July 18, 2026 |
| Final Vendor Selection | July 25, 2026 |
| Contract Negotiation | July 28 — August 15, 2026 |
| Contract Signing (Target) | August 18, 2026 |
| Project Kickoff (Target) | September 1, 2026 |

### 17.2 Submission Format

1. **Proposal must be submitted electronically** via email to: **info@1000fix.com** with subject line: "**ERP RFP Response — [Vendor Company Name] — 1000FIX-ERP-RFP-2026-001**"
2. **Format**: PDF document (main proposal) + Excel spreadsheet (pricing and requirement response matrix)
3. **Language**: English (Bengali supplementary materials accepted)
4. **Page Limit**: No strict limit, but concise and well-organized proposals are preferred
5. **File Size**: Maximum 50 MB per email; use file-sharing link for larger submissions

### 17.3 Proposal Structure

Vendors must organize their proposals as follows:

| Section | Required Content |
|---|---|
| **Cover Letter** | Executive summary, commitment statement, authorized signatory |
| **Section 1: Company Profile** | Per Section 14 (Vendor Qualifications) of this RFP |
| **Section 2: Solution Overview** | Architecture, technology, modules, differentiators |
| **Section 3: Functional Response** | Requirement-by-requirement response (S/C/D/T/N) with explanations |
| **Section 4: Technical Response** | Architecture, security, performance, integration approach |
| **Section 5: Portal Suite Response** | Detailed portal capabilities and approach |
| **Section 6: Implementation Plan** | Methodology, phases, timeline, team, risk mitigation |
| **Section 7: Training & Change Management** | Training approach, materials, change management plan |
| **Section 8: Support & Maintenance** | SLAs, team, processes, escalation |
| **Section 9: Pricing** | Per Section 15 (Budget & Pricing) of this RFP |
| **Section 10: References & Case Studies** | Per Section 14.4 of this RFP |
| **Section 11: Exceptions & Assumptions** | Any deviations from RFP requirements with justification |
| **Appendix A** | Detailed requirement response matrix (Excel) |
| **Appendix B** | Proposed team resumes |
| **Appendix C** | Sample project plan |
| **Appendix D** | Product screenshots/demo materials |

### 17.4 Vendor Questions

- All questions must be submitted in writing to **info@1000fix.com** by April 7, 2026
- Questions and answers will be shared with all participating vendors (anonymized)
- No individual pre-submission meetings will be conducted
- A vendor briefing webinar will be scheduled within 2 weeks of RFP issuance (date TBD)

### 17.5 Clarifications

1000FiX reserves the right to:
- Request clarifications on submitted proposals
- Conduct due diligence on any aspect of the proposal
- Request additional demonstrations or proof-of-concept
- Modify timelines as needed with reasonable notice to all vendors
- Accept or reject any or all proposals at its sole discretion

---

## 18. TERMS & CONDITIONS

### 18.1 General Terms

1. **No Obligation**: This RFP does not commit 1000FiX to award a contract, pay any costs incurred in proposal preparation, or procure or contract for any services.

2. **Confidentiality**: All information in this RFP and all vendor responses are confidential. Vendors may not disclose any aspect of this RFP process to third parties without written consent.

3. **Intellectual Property**: All customizations, configurations, and developments created specifically for 1000FiX during the project shall be owned by 1000FiX. The vendor retains ownership of their core product intellectual property.

4. **Data Ownership**: All data entered into or generated by the ERP system belongs exclusively to 1000FiX. The vendor must provide full data export capability in standard formats upon contract termination.

5. **Non-Exclusivity**: This RFP does not grant exclusive rights to any vendor. 1000FiX may engage multiple vendors for different components if deemed beneficial.

6. **Validity Period**: Proposals must remain valid for a minimum of **180 days** from the submission deadline.

7. **Governing Law**: Any contract arising from this RFP shall be governed by the laws of the People's Republic of Bangladesh.

8. **Dispute Resolution**: Disputes shall be resolved through good-faith negotiation first, followed by mediation, and if necessary, arbitration under the Arbitration Act of Bangladesh.

### 18.2 Contractual Expectations

The selected vendor will be required to enter into a formal contract that includes:

- Detailed statement of work (SOW) for each phase
- Service Level Agreements (SLAs) with penalty/incentive structure
- Milestone-based payment terms
- Warranty and defect liability provisions
- Performance bond or bank guarantee (to be negotiated)
- Termination clauses with adequate transition support
- Non-disclosure agreement (NDA)
- Business continuity provisions

### 18.3 Compliance Requirements

Vendors must comply with:

- All applicable laws of Bangladesh
- Bangladesh ICT Act, 2006 (and amendments)
- Bangladesh Digital Security Act, 2018
- National Board of Revenue (NBR) tax and VAT regulations
- Bangladesh Labour Act, 2006 (for on-site staff)
- Any applicable data privacy and protection regulations

---

## 19. APPENDICES

### Appendix A: Current Business Process Flows

#### A.1 Service Order Lifecycle (Current State)

```
Customer Contact (Phone/Walk-in/Website)
    ↓
Manual Order Entry (Spreadsheet/Paper)
    ↓
Manual Technician Assignment (Phone/WhatsApp)
    ↓
Service Execution (No Real-time Tracking)
    ↓
Manual Completion Reporting
    ↓
Paper Invoice Generation
    ↓
Manual Payment Collection
    ↓
Manual Entry in Accounting System
```

#### A.2 Service Order Lifecycle (Desired Future State with ERP)

```
Multi-Channel Request (Portal/Phone/WhatsApp/Chatbot/Walk-in/Email)
    ↓
Automated Order Creation with Device & Customer Validation
    ↓
AI-Powered Technician Assignment (Skills + Location + Availability + Priority)
    ↓
Real-Time GPS Tracking & Customer Notifications
    ↓
Mobile Digital Service Form Completion with Photos & E-Signature
    ↓
Automatic Invoice Generation & Multi-Channel Payment
    ↓
Automated Accounting Entry & Revenue Recognition
    ↓
Automated Customer Feedback Request & Quality Scoring
    ↓
Warranty Claim Auto-Generation (if applicable)
    ↓
Analytics & Business Intelligence Updates
```

### Appendix B: Service Center Network

1000FiX operates **51+ service centers** across all 8 divisions of Bangladesh. A complete list of service center locations, addresses, and operational hours will be provided to shortlisted vendors during the detailed design phase.

**Key Regional Hubs:**
- **Dhaka Division**: Corporate HQ + Central Warehouse + Multiple Service Centers
- **Chittagong Division**: Regional Hub + Multiple Service Centers
- **Rajshahi Division**: Regional Hub + Service Centers
- **Khulna Division**: Regional Hub + Service Centers
- **Other Divisions**: Service Centers with standard operations

### Appendix C: Authorized Brand Partner Matrix

| Brand | Product Categories Serviced | Warranty Type |
|---|---|---|
| Dell | Laptops, Desktops, Servers, Monitors | Full Warranty + Extended |
| HP | Laptops, Desktops, Printers | Full Warranty + Extended |
| Lenovo | Laptops, Desktops | Full Warranty |
| Acer | Laptops, Desktops | Full Warranty |
| Samsung | Mobile, Tablet, TV, Appliances | Full Warranty |
| Xiaomi | Mobile, Smart Devices | Full Warranty |
| Huawei | Mobile, Networking | Full Warranty |
| Honor | Mobile | Full Warranty |
| Sony | Laptops, Electronics | Full Warranty |
| Toshiba | Laptops | Full Warranty |
| Gigabyte | Motherboards, Components | Full Warranty |
| Microsoft | Surface Devices | Full Warranty |
| BenQ | Monitors, Projectors | Full Warranty |
| Epson | Printers | Full Warranty |
| Intel | Components | Full Warranty |
| TwinMOS | Memory, Storage | Full Warranty |
| Delux | Peripherals | Full Warranty |

### Appendix D: Key Performance Indicators (KPIs) Dashboard Requirements

The ERP system must track and display the following KPIs:

**Operational KPIs:**
- Total service orders: daily/weekly/monthly/yearly
- Service orders by status (pipeline view)
- Average turnaround time by service type
- First-time fix rate
- Rework rate
- SLA compliance rate
- Technician utilization rate
- Average jobs per technician per day

**Financial KPIs:**
- Total revenue: daily/weekly/monthly
- Revenue by service type, brand, branch
- Warranty revenue vs. out-of-warranty revenue
- Average revenue per service order
- Collection rate and aging
- Cost per service order (labor + parts + overhead)
- Gross margin by service type and branch
- Outstanding warranty claims value

**Customer KPIs:**
- Customer satisfaction (CSAT) score
- Net Promoter Score (NPS)
- Customer retention rate
- New customer acquisition rate
- Customer complaint rate and resolution time
- Repeat customer percentage
- Privilege program enrollment and renewal rate

**Inventory KPIs:**
- Stock value by location
- Stock turnover ratio
- Dead stock percentage
- Stockout rate
- Inter-branch transfer volume
- Order fulfillment rate (parts availability at first visit)

**HR KPIs:**
- Employee headcount and turnover
- Technician certification status
- Training completion rate
- Attendance compliance
- Average performance score

### Appendix E: Glossary of Terms

| Term | Definition |
|---|---|
| **1000FiX** | 1000FiX Services Limited, the issuing organization |
| **AMC** | Annual Maintenance Contract — periodic maintenance agreement |
| **RAMC** | Residential Annual Maintenance Contract — home appliance maintenance packages |
| **SLA** | Service Level Agreement — agreed performance standards |
| **CSAT** | Customer Satisfaction Score |
| **NPS** | Net Promoter Score |
| **BDT** | Bangladeshi Taka — national currency |
| **NBR** | National Board of Revenue — Bangladesh tax authority |
| **VAT** | Value Added Tax |
| **TDS** | Tax Deducted at Source |
| **RBAC** | Role-Based Access Control |
| **MFA** | Multi-Factor Authentication |
| **SSO** | Single Sign-On |
| **PWA** | Progressive Web Application |
| **API** | Application Programming Interface |
| **SaaS** | Software as a Service |
| **RPO** | Recovery Point Objective — maximum acceptable data loss in time |
| **RTO** | Recovery Time Objective — maximum acceptable system downtime |
| **NTE** | Not-to-Exceed — maximum cost limit without additional approval |
| **CAPA** | Corrective and Preventive Action |
| **NCR** | Non-Conformance Report |
| **PII** | Personally Identifiable Information |
| **BST** | Bangladesh Standard Time (UTC+6) |
| **B2B** | Business-to-Business |
| **B2C** | Business-to-Consumer |
| **OEM** | Original Equipment Manufacturer |
| **GL** | General Ledger |
| **AR** | Accounts Receivable |
| **AP** | Accounts Payable |
| **PO** | Purchase Order |
| **GRN** | Goods Receipt Note |
| **FIFO** | First In, First Out (inventory valuation method) |
| **RTV** | Return to Vendor |
| **IoT** | Internet of Things |
| **BI** | Business Intelligence |
| **ERP** | Enterprise Resource Planning |

---

## DOCUMENT REVISION HISTORY

| Version | Date | Author | Description |
|---|---|---|---|
| 1.0 | March 17, 2026 | 1000FiX Services Limited | Initial RFP Release |

---

**END OF DOCUMENT**

---

*This RFP document is the property of 1000FiX Services Limited. All rights reserved.*

*1000FiX Services Limited*
*586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216, Bangladesh*
*Hotline: 16743 | Phone: 09644-300600 | Email: info@1000fix.com*
*Website: https://1000fix.com*
*ISO 9001:2015 Certified — Bangladesh's Largest After-Sales Service Provider*
