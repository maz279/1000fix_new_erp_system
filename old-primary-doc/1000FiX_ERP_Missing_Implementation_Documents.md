# 1000FiX ERP System — Missing Implementation Documents Checklist

**Document ID:** 1000FIX-ERP-IMPL-DOCS-2026-001
**Version:** 1.0
**Date:** March 18, 2026
**Prepared For:** UniSoft Development Team (2 Full-Stack Developers)
**Classification:** CONFIDENTIAL — Internal Use Only

---

## 1. Executive Summary

The 1000FiX ERP project currently has **5 strategic/business-level documents** that define WHAT to build and WHY:

| # | Existing Document | Purpose |
|---|---|---|
| 1 | Comprehensive RFP | Scope, timeline (18 months), budget ($150K–$350K), vendor criteria |
| 2 | Comprehensive BRD | 190+ functional requirements across 11 modules, business rules |
| 3 | Comprehensive URD | 20 user personas, 67+ user stories, 12 journey maps, usability specs |
| 4 | Implementation Strategy (Odoo 19 CE) | 5-layer tech stack, OCA module mapping, phased rollout plan |
| 5 | Technology Stack Specification | Detailed architecture, 20 custom modules (CD-01 to CD-20), tool versions |

**The Gap:** These documents answer WHAT and WHY but not HOW. For the 2-person UniSoft full-stack developer team to begin actual coding, **19 additional technical implementation guide documents** are required. Without these, developers will waste significant time guessing architecture, making contradictory design decisions, and building on unstable foundations.

**Critical Note:** The existing documents assume a **6-person team** (2 senior Odoo devs, 2 Flutter devs, 1 DevOps, 1 BA/QA). The actual team is **2 full-stack developers (1 team leader)**. Document #5 (Sprint Planning) must re-baseline the timeline accordingly.

---

## 2. Document Priority Overview

| Priority | When Needed | Count | Documents |
|---|---|---|---|
| **P1 — BLOCKING** | Before Day 1 of development | 5 | Dev Environment, Module Architecture, Database Schema, Git Workflow, Sprint Planning |
| **P2 — CRITICAL** | Within first sprint (Weeks 1–2) | 3 | API Specification, Keycloak SSO Guide, UI/UX Design System |
| **P3 — PHASE-SPECIFIC** | Before the relevant phase begins | 8 | Integration Specs, Flutter Architecture, Testing Strategy, Data Migration, DevOps Pipeline, n8n Workflows, Offline Sync Architecture, AI Dispatch Algorithm |
| **P4 — IMPORTANT** | Ongoing / before go-live | 3 | Bengali Localization Guide, OCA v19 Compatibility Report, Operational Runbook |

**Total: 19 documents | Estimated 360–500 pages of technical content**

---

## 3. PRIORITY 1 — MUST-HAVE BEFORE DAY 1

These documents are **blocking**. Without them, developers cannot start productive work.

---

### Document 1: ERP Development Environment Setup Guide

**Priority:** P1 — Before Day 1
**Estimated Size:** 15–20 pages
**Audience:** Both developers

**Why It Is Essential:**
On Day 1, each developer needs to go from a blank Linux desktop to a fully running Odoo 19 CE instance with OCA modules, PostgreSQL 16, Keycloak, n8n, Redis, Traccar, and all supporting services connected and verified. The existing documents name these tools but never explain how to install, configure, or interconnect them locally.

**What It Must Contain:**

1. **Linux Base System Setup**
   - Recommended distribution (Ubuntu 22.04 LTS or Fedora 39+)
   - System packages: `python3.12`, `python3.12-venv`, `node18+`, `wkhtmltopdf`, `libpq-dev`, `libxml2-dev`, `libxslt1-dev`, `libsasl2-dev`, `libldap2-dev`
   - PostgreSQL 16 installation and initial database creation (`createdb` with Odoo-specific locale settings: `en_US.UTF-8` or `bn_BD.UTF-8`)

2. **Odoo 19 CE Source Installation**
   - Clone from GitHub (`odoo/odoo` branch `19.0`) — source install, not pip, for debugging capability
   - Python virtual environment with `pip install -r requirements.txt`
   - `odoo.conf` template with all local paths, addons_path, database settings
   - First-run verification: `./odoo-bin -c odoo.conf -d odoo19_dev --stop-after-init`

3. **OCA Module Installation**
   - Cloning procedure for each required OCA repository (branch `19.0`):
     - `field-service` (33 modules), `helpdesk` (28 modules), `management-system` (33 modules)
     - `operating-unit`, `hr`, `payroll`, `dms`, `reporting-engine`, `mis-builder`
   - Adding OCA repos to `addons_path` in `odoo.conf`
   - Module installation verification commands

4. **Supporting Services via Docker Compose**
   - Docker Compose file for services developers don't modify but need running:
     - Keycloak 26.x (SSO/identity)
     - n8n 1.x (workflow automation)
     - Redis 7.x (caching/sessions)
     - Traccar 6.x (GPS tracking)
     - Novu 2.x (notifications)
   - Port mapping and network configuration
   - Health check endpoints

5. **VS Code Configuration**
   - Required extensions: Python (ms-python), Pylance, Odoo Snippets, XML Tools, Docker, GitLens, REST Client, OWL DevTools
   - `launch.json` for Odoo debug mode (attach to Odoo process)
   - `settings.json` for pylint-odoo integration, Python path pointing to venv
   - OWL component debugging setup

6. **Development Server & HMR**
   - Running Odoo in dev mode: `./odoo-bin --dev=all` (auto-reload Python, reload XML assets)
   - OWL hot reload configuration for frontend components
   - Chrome DevTools OWL extension for component inspection
   - Browser preview setup

7. **Environment Variables & Configuration**
   - `.env` file template with all required variables
   - Database connection strings, API keys (placeholder), service URLs
   - How to switch between dev/staging configurations

8. **Verification Checklist**
   - 10-step checklist: "Run these commands to confirm your environment is fully working"
   - Expected output for each verification step
   - Estimated setup time: 4–6 hours per developer

**Cross-References:**
- Tech Stack Spec, Section 3.1 (Platform specifications: Python 3.12, PostgreSQL 16, Odoo 19.0)
- Tech Stack Spec, Section 6.11 (Complete tool version matrix)
- Implementation Strategy, Section 9.3 (Docker deployment architecture)

---

### Document 2: Odoo 19 CE Module Architecture & Project Structure Guide

**Priority:** P1 — Before Day 1
**Estimated Size:** 20–25 pages
**Audience:** Both developers

**Why It Is Essential:**
Odoo module development has strict conventions (model inheritance, view XML, security CSV files, manifest files). A developer who knows Python but not Odoo will immediately make structural mistakes that cascade through the entire project. The 20 custom modules (CD-01 through CD-20) all need to follow Odoo's conventions precisely.

**What It Must Contain:**

1. **Odoo Module Directory Structure**
   - Standard layout: `__manifest__.py`, `__init__.py`, `models/`, `views/`, `security/`, `data/`, `static/`, `controllers/`, `wizard/`, `reports/`, `tests/`
   - Purpose and conventions for each directory
   - Example custom module skeleton with all required files

2. **Module Naming Conventions for 1000FiX**
   - Naming pattern for 20 custom modules (e.g., `1000fix_privilege_program`, `1000fix_mushak_invoice`, `1000fix_bd_payroll`, `1000fix_ai_dispatch`)
   - Mapping of CD-01 through CD-20 codes to module technical names

3. **`__manifest__.py` Templates**
   - Complete manifest template with proper dependency chains
   - Examples: How CD-05 depends on `crm` and `sale`, how CD-02 depends on `account` and `l10n_bd`
   - Version numbering scheme aligned with Odoo 19

4. **Model Development Patterns**
   - `_inherit` vs `_inherits` vs delegation inheritance — when to use each, with 1000FiX examples
   - Adding fields to standard Odoo models vs creating new custom models
   - Computed fields, onchange methods, constraints — Odoo-specific patterns
   - Multi-company and multi-branch (Operating Unit) patterns

5. **View Development (XML)**
   - Form views, tree/list views, kanban views, search views
   - View inheritance: `<field position="after">`, `<xpath>` expressions
   - Priority attributes for controlling view inheritance order
   - QWeb templates for portal pages

6. **OWL 2 Frontend Components**
   - OWL component structure for Odoo 19 (different from Odoo 16/17)
   - Custom widget development for non-standard UI (dispatch board, walk-in queue, leaderboard)
   - Static asset bundling and registration

7. **How to Extend OCA Modules Without Forking**
   - Using `_inherit` to add fields/methods to `fieldservice.order`, `helpdesk.ticket`, etc.
   - Adding views/menus to OCA modules via XML inheritance
   - When forking is unavoidable and how to manage it

8. **Git Repository Structure**
   - Monorepo vs multi-repo decision and rationale
   - Addons path organization: separating L1 (Odoo CE), L2 (OCA), L3 (third-party), and L5 (custom) modules
   - `.gitignore` template for Odoo development

9. **Configuration Management**
   - `odoo.conf` management across dev/staging/production environments
   - Data files vs configuration: what goes in XML data files vs system parameters

**Cross-References:**
- Tech Stack Spec, Section 7.2 (20 custom module definitions with dependencies)
- Tech Stack Spec, Section 3.2 (OWL 2 framework architecture)
- Implementation Strategy, Section 8.1 (Custom development specifications)

---

### Document 3: Database Schema & Data Model Specification

**Priority:** P1 — Before Day 1
**Estimated Size:** 40–60 pages
**Audience:** Both developers (critical alignment document)

**Why It Is Essential:**
The BRD defines 190+ functional requirements across 11 modules. Odoo has its own ORM with specific model conventions. Without a shared data model specification, two developers working on interconnected modules will make contradictory field definitions, model relationships, and naming choices — resulting in costly rework.

**What It Must Contain:**

1. **Entity Relationship Diagrams (ERDs)**
   - One ERD per module scope: SRM, FSM, INV, CRM, FIN, HRM, CWM, SCM, QMS
   - Showing relationships between standard Odoo models, OCA models, and custom models
   - Cardinality and relationship types (Many2one, One2many, Many2many)

2. **Standard Odoo Models Used (Mapping)**
   - Which existing Odoo/OCA models satisfy which BRD requirements
   - Example: `fieldservice.order` for service orders, `helpdesk.ticket` for complaints, `stock.warehouse` for branch inventory
   - Fields to ADD to existing models via inheritance

3. **Custom Model Definitions (All 20 CD Modules)**
   - For each custom module (CD-01 through CD-20):
     - Model name (`_name`)
     - Fields with types, sizes, constraints, defaults, help text
     - Computed fields with dependency declarations
     - Business logic methods (signatures, not full implementation)
     - Access control groups
   - Key models include:
     - **CD-02 (Mushak 6.3):** Fields on `account.move` — BIN, TIN, Mushak reference number, VAT challan fields
     - **CD-03 (BD Payroll):** Salary structure model, tax slab tables, provident fund fields, BEFTN export fields
     - **CD-05 (Privilege Program):** Membership tier model, discount rule model, customer-membership relation, points/cashback ledger
     - **CD-06 (AI Dispatch):** Scoring weights model, optimization constraints, route cache model
     - **CD-09 (Warranty Claims):** Claim model fields, brand partner mappings, claim status workflow states

4. **Multi-Branch Data Architecture**
   - How `operating.unit` (OCA module) connects to every transactional model
   - Record rules for branch-level data isolation
   - Cross-branch visibility rules for managers vs branch staff

5. **Data Migration Field Mapping**
   - Source columns from legacy spreadsheets/systems → target Odoo model fields
   - Data type conversions, format transformations (date formats, phone number normalization)
   - Required field default values for historical records

6. **Sample Data Fixtures**
   - Development seed data for each module (minimum viable data to test workflows)
   - Test data for 3–5 sample service orders, customers, technicians, inventory items
   - Bengali text test data

7. **Database Configuration**
   - PostgreSQL 16 settings optimized for Odoo (shared_buffers, effective_cache_size, work_mem)
   - Indexes for frequently queried fields (customer phone lookup, service order status queries)
   - Bengali text collation and full-text search configuration

**Cross-References:**
- BRD, Sections 8–13 (All 190+ functional requirements that must map to data models)
- Tech Stack Spec, Section 7.2 (Custom module definitions CD-01 through CD-20)
- Tech Stack Spec, Section 8 (Requirement-to-technology mapping matrix)
- URD, Section 6–10 (67+ user stories defining data inputs/outputs)

---

### Document 4: Git Workflow, Coding Standards & Code Review Process

**Priority:** P1 — Before Day 1
**Estimated Size:** 10–15 pages
**Audience:** Both developers

**Why It Is Essential:**
With only 2 developers, every merge conflict, broken build, or ambiguous code convention costs disproportionate time. This process document prevents the small team from falling into chaos and ensures consistent, maintainable code.

**What It Must Contain:**

1. **Git Branching Strategy**
   - `main` (production-ready), `staging` (pre-release), `develop` (integration)
   - Feature branches: `feature/CD-05-privilege-program`, `feature/CD-02-mushak-invoice`
   - Hotfix branches: `hotfix/urgent-fix-description`
   - Branch naming convention tied to custom module IDs (CD-01 through CD-20)

2. **Commit Message Format**
   - Conventional Commits standard: `feat(CD-05): add loyalty tier calculation model`
   - Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`
   - Scope: module ID or general area (`core`, `config`, `deploy`)

3. **Code Review Process (2-Person Team)**
   - Author creates PR → other developer reviews → no self-merges to `main`
   - Review checklist:
     - Security: No SQL injection via ORM bypass, no hardcoded credentials
     - Performance: No N+1 queries, proper `sudo()` usage
     - Odoo conventions: Proper `_inherit`/`_name`, field naming, ACL files
     - Bengali string handling: No hardcoded UI strings, all in `.po` files
   - Turnaround time target: reviews within 4 hours

4. **Python Coding Standards**
   - PEP 8 baseline + Odoo-specific additions
   - Model naming: snake_case with dot separators (`1000fix.privilege.tier`)
   - Field naming conventions (no `x_` prefix for custom module fields — only for studio fields)
   - Import ordering: standard lib → third-party → odoo → odoo.addons
   - Pylint-odoo configuration and pre-commit hooks

5. **XML/OWL Coding Standards**
   - XML indentation (4 spaces), `priority` attributes for view inheritance
   - Template naming conventions for QWeb
   - JavaScript/OWL coding standards (ES6+, OWL 2 patterns)

6. **Release & Tagging Strategy**
   - Semantic versioning: `v1.0.0` for Phase 1 go-live, `v2.0.0` for Phase 2, etc.
   - Tag format aligned with the 6-phase rollout plan
   - Changelog generation from conventional commits

**Cross-References:**
- Implementation Strategy, Section 11.2 (6-phase rollout timeline)
- Tech Stack Spec, Section 3.1 (Python 3.12, OWL 2 framework)

---

### Document 5: Sprint Planning & Task Breakdown for 2-Person Team

**Priority:** P1 — Before Day 1
**Estimated Size:** 20–30 pages
**Audience:** Team Leader (primary), Developer (reference)

**Why It Is Essential:**
The Implementation Strategy defines an 18-month/6-phase roadmap but assumes a **6-person team**. With 2 full-stack developers, task sequencing, parallelism, and timeline must be fundamentally re-baselined. Without this, the team will either commit to an impossible schedule or waste time on lower-priority items.

**What It Must Contain:**

1. **Re-Baselined Timeline**
   - Honest assessment: 18 months with 2 devs vs 6 devs
   - Three options analysis:
     - (a) Extend timeline to 24–30 months
     - (b) Narrow Phase 1 scope (defer Privilege Program, Walk-in Queue to Phase 2)
     - (c) Add a third developer mid-project for Flutter app (CD-01 alone is 16–20 person-weeks)
   - Recommended option with justification

2. **Phase 1 Sprint Breakdown (Months 1–4)**
   - 2-week sprint cadence with specific deliverables per sprint
   - Each sprint card: Odoo modules to install/configure, custom module code to write, tests to pass
   - Sprint 1: Environment setup, Odoo CE installation, OCA module verification
   - Sprint 2: Core models (service order, customer, device), base views
   - Sprint 3–4: Service center agent workflow end-to-end
   - Sprint 5–6: Dispatch workflow, technician assignment
   - Sprint 7–8: Inventory basics, integration testing

3. **Task Ownership & Parallelization**
   - Developer A (Team Leader) vs Developer B — who does what in parallel
   - Dependency map: cannot start CD-05 until CRM module is configured
   - Critical path identification

4. **Definition of Done (Per Task)**
   - Unit tests pass (`odoo.tests`)
   - Code reviewed by other developer
   - Demo-able in staging environment
   - Bengali UI strings added (even if placeholder)

5. **Sprint Ceremonies (Lean, for 2 People)**
   - Daily standup: 10-min async update (Slack/chat)
   - Sprint planning: 1 hour every 2 weeks
   - Sprint review/demo: 30 min every 2 weeks
   - Retrospective: 15 min every 2 weeks

6. **Risk Register Per Sprint**
   - OCA module v19 compatibility issues
   - Third-party API documentation gaps (bKash, SSLCOMMERZ)
   - Odoo learning curve for developers new to the framework
   - Scope creep from stakeholder feedback

7. **Milestone Gates**
   - Phase 1 → Phase 2 gate criteria: what must be TRUE before proceeding
   - Phase 2 → Phase 3 gate criteria
   - Each gate tied to BRD acceptance criteria

**Cross-References:**
- Implementation Strategy, Section 11.2 (Phase-level week-by-week deliverables for 6-person team)
- Implementation Strategy, Section 8.1 (Custom development effort estimates per module)
- Tech Stack Spec, Section 7.2 (Module dependency chains)
- BRD, Section 20 (Acceptance criteria)

---

## 4. PRIORITY 2 — NEEDED WITHIN FIRST SPRINT (Weeks 1–2)

These documents can be drafted during the first sprint while developers set up infrastructure, but must be ready before significant custom code is written.

---

### Document 6: Odoo JSON-RPC API Specification & Integration Contract

**Priority:** P2 — Week 2
**Estimated Size:** 25–35 pages
**Audience:** Both developers

**Why It Is Essential:**
The system has 3 API consumers: Next.js web platform (existing public website), Flutter mobile app (CD-01), and n8n workflows. The Tech Stack mentions Odoo JSON-RPC API endpoints but does not define request/response schemas, authentication headers, error formats, or pagination. Without this contract, the API producers (Odoo controllers) and consumers (Flutter/Next.js) will build incompatible interfaces.

**What It Must Contain:**

1. **Authentication Flow**
   - Odoo JSON-RPC authentication: `/web/session/authenticate`
   - Keycloak JWT token → Odoo session bridge (or direct API key approach)
   - Token refresh flow for mobile app
   - API key management for n8n service account

2. **Endpoint Catalog — Flutter Mobile App (CD-01)**
   - Job queue: `GET /api/v1/technician/jobs` — daily assigned jobs with customer info
   - Job status update: `PUT /api/v1/jobs/{id}/status` — status transitions with validation
   - Photo upload: `POST /api/v1/jobs/{id}/photos` — multipart upload with compression specs
   - GPS position: `POST /api/v1/technician/location` — lat/lng with timestamp
   - Parts consumption: `POST /api/v1/jobs/{id}/parts` — record parts used
   - E-signature: `POST /api/v1/jobs/{id}/signature` — base64 encoded image
   - Offline sync batch: `POST /api/v1/sync/batch` — bulk upload queued changes
   - Parts catalog: `GET /api/v1/parts/catalog` — for offline caching

3. **Endpoint Catalog — Next.js Web Platform**
   - Service order creation: `POST /api/v1/service-orders`
   - Availability check: `GET /api/v1/availability`
   - Payment confirmation webhook: `POST /api/v1/payments/confirm`
   - Customer tracking: `GET /api/v1/tracking/{order_id}`
   - Invoice retrieval: `GET /api/v1/invoices/{id}`

4. **Request/Response Schemas**
   - JSON schema definitions for every endpoint
   - TypeScript types (for Next.js) and Dart classes (for Flutter)
   - Pagination format: cursor-based vs offset-based
   - Date/time format: ISO 8601 with timezone (Asia/Dhaka)
   - Currency format: BDT with 2 decimal places

5. **Error Response Standard**
   - Consistent error envelope: `{ "error": { "code": "...", "message": "...", "details": [...] } }`
   - Error code catalog (validation errors, auth errors, business rule violations)
   - HTTP status code usage conventions

6. **Webhook Payloads**
   - Service order created/updated webhook
   - Payment received webhook
   - Technician dispatched webhook
   - SLA breach webhook
   - Payload format, retry policy, signature verification

**Cross-References:**
- Tech Stack Spec, Section 9.2 (8 example API endpoints and 4 webhook events)
- BRD, Section 15 (Integration requirements)
- URD, Section 6–10 (User stories defining data flows)

---

### Document 7: Keycloak SSO & Security Implementation Guide

**Priority:** P2 — Week 2
**Estimated Size:** 15–20 pages
**Audience:** Team Leader (primary)

**Why It Is Essential:**
Keycloak 26.x is the SSO/identity layer connecting Odoo, Next.js, Flutter, Metabase, and n8n. Security misconfiguration on Day 1 creates rework cascading through the entire project. The Tech Stack describes Keycloak at capability level but not at implementation level.

**What It Must Contain:**

1. **Keycloak Realm Configuration**
   - Realm name: `1000fix`
   - Login theme customization (1000FiX branding, Bengali language)
   - Email/SMS verification settings
   - Password policy (complexity, expiry)

2. **Client Configurations (One Per Application)**
   - Odoo Backend: confidential client, OIDC authorization code flow
   - Flutter Mobile App: public client, PKCE flow
   - Next.js Portal: confidential client, authorization code flow
   - Metabase: confidential client, OIDC
   - n8n: confidential client, service account / client credentials

3. **Role Definitions Mapped to BRD User Roles**
   - Mapping of 20 URD personas to Keycloak realm roles:
     - `admin`, `dispatcher`, `technician_senior`, `technician_junior`
     - `branch_manager`, `operations_manager`, `finance_officer`, `finance_manager`
     - `hr_officer`, `hr_manager`, `inventory_manager`, `procurement_officer`
     - `it_admin`, `customer`, `corporate_client`, `vendor`, `brand_partner`, `ceo`
   - Composite roles for role hierarchies

4. **RBAC Implementation in Odoo**
   - Keycloak roles → Odoo `res.groups` mapping
   - `ir.model.access.csv` templates for each custom module
   - `ir.rule` (record rules) for multi-branch data isolation via Operating Unit
   - Menu visibility per role

5. **MFA Configuration**
   - TOTP (Google Authenticator) for admin, finance, and HR roles
   - Optional MFA for other roles

6. **Session Management**
   - Access token lifetime, refresh token lifetime
   - Single sign-out across all applications
   - Mobile app token storage (Flutter secure storage)

7. **Odoo Integration**
   - `auth_oidc` OCA module configuration for Keycloak
   - User auto-provisioning from Keycloak to Odoo `res.users`
   - Mapping Keycloak groups to Odoo groups

**Cross-References:**
- Tech Stack Spec, Section 6.8 (Keycloak architecture description)
- URD, Section 4 (User roles and access matrix — 20 roles with CRUD permissions)
- BRD, Section 14 (Security and access control requirements)

---

### Document 8: UI/UX Design System & Wireframes

**Priority:** P2 — Week 2
**Estimated Size:** 30–40 pages
**Audience:** Both developers

**Why It Is Essential:**
The URD defines 20 personas and 67+ user stories with detailed acceptance criteria, but provides **zero visual design**. Developers will need to make hundreds of UI decisions for Odoo backend views, portal views, and the Flutter app. Without a design system, the two developers will produce inconsistent interfaces that fail UAT usability testing (SUS score ≥75 requirement).

**What It Must Contain:**

1. **Design System Foundation**
   - Color palette: Primary, secondary, accent colors aligned with 1000FiX brand
   - Typography: Bengali font selection (Noto Sans Bengali or SolaimanLipi), English font, size scale
   - Icon set: consistent iconography for all modules
   - Spacing and grid system
   - Component states: default, hover, active, disabled, error, loading

2. **Odoo Backend View Templates**
   - Service Order form view wireframe (customer info, device info, service type, status, timeline)
   - Dispatch Board kanban/map wireframe (unassigned queue, technician map, drag-and-drop)
   - Inventory dashboard wireframe (stock levels by branch, color-coded alerts)
   - Financial reconciliation dashboard wireframe
   - HR payroll batch processing view wireframe

3. **Custom OWL Component Designs**
   - Dispatch drag-and-drop board (AI suggestion indicators, manual override)
   - Walk-in customer queue display (token numbers, estimated wait time)
   - Technician performance leaderboard (gamification elements)
   - Real-time map component (technician locations with 30-sec refresh)
   - SLA countdown timer widget

4. **Flutter Mobile App Screens (CD-01)**
   - Login / Keycloak auth flow screens
   - Daily job queue (list view with priority indicators)
   - Job detail screen (customer info, device history, navigation button)
   - Diagnostic checklist screen (by device type)
   - Photo capture and annotation screen
   - Barcode/QR scanner screen
   - E-signature capture screen
   - Parts consumption form
   - Sync status indicator
   - Offline mode banner

5. **Customer Portal Screens (Responsive)**
   - 3-step service booking wizard
   - Real-time technician GPS tracking page
   - Service history with invoice download
   - Payment page (bKash/Nagad/Card selection)
   - Feedback/rating submission

6. **Bengali Language UI Patterns**
   - Bengali numeral display options (Bengali ১২৩ vs Western 123 — decision needed)
   - Date format: DD/MM/YYYY with Bengali month names
   - Currency display: ৳1,23,456 (Bangladesh lakh format)
   - Form labels in Bengali with English tooltips for technical terms
   - Error messages in Bengali

7. **Accessibility Specifications**
   - WCAG 2.1 AA compliance checklist per component
   - Color contrast ratios (4.5:1 normal text, 3:1 large text)
   - Touch targets: 44×44 px minimum (mobile)
   - Focus ring visibility, keyboard navigation order
   - Screen reader considerations for Bengali content

**Cross-References:**
- URD, Section 12 (Usability requirements — performance, navigation, mobile-first, error handling, accessibility)
- URD, Section 13 (Localization — Bengali language, financial formats, payment methods)
- URD, Section 3 (20 user personas with tech proficiency levels 1–5)
- URD, Sections 6–10 (67+ user stories defining screen-level interactions)

---

## 5. PRIORITY 3 — NEEDED BEFORE SPECIFIC PHASES

These documents are phase-specific and must be ready before the phase they support begins.

---

### Document 9: Integration Technical Specifications

**Priority:** P3 — Before Phase 2 (Month 5)
**Estimated Size:** 30–40 pages
**Audience:** Both developers

**Why It Is Essential:**
The system integrates with bKash, Nagad, SSLCOMMERZ, Google Maps, WhatsApp Business API, Bangladesh SMS gateways, Firebase, brand partner portals, and biometric devices. The Tech Stack names these integrations but does not provide endpoint URLs, authentication flows, sandbox credentials, or data mapping. Developers cannot implement integrations from names alone.

**What It Must Contain:**

1. **bKash Payment Gateway (CD-08)**
   - Sandbox environment URL and merchant credentials procurement process
   - Payment flow: Create Payment → Execute Payment → Query Payment
   - OTP-based customer authorization sequence diagram
   - IPN (Instant Payment Notification) callback URL format and payload
   - Reconciliation API for end-of-day settlement
   - BDT amount constraints (min/max), transaction fee structure
   - Error codes and retry logic

2. **Nagad Payment Gateway (CD-08)**
   - Merchant registration and sandbox setup
   - Direct debit flow vs checkout redirect flow
   - Callback/webhook handling
   - Reconciliation and settlement

3. **SSLCOMMERZ Payment Gateway (CD-08)**
   - Session initiation API
   - Hosted checkout vs direct API integration — decision and rationale
   - Success, fail, cancel, and IPN callback URL handling
   - IPN hash validation for security
   - Supported card types, EMI/installment configuration
   - Multi-currency handling (BDT only)

4. **Google Maps Platform**
   - APIs needed: Geocoding, Directions, Distance Matrix, Places, Maps SDK (Flutter)
   - API key creation, restriction (HTTP referrer for web, app signing for mobile)
   - Billing alerts and quota management
   - Bangladesh-specific considerations (coverage, accuracy)

5. **WhatsApp Business API**
   - Meta Cloud API vs Business Solution Provider (BSP) — decision
   - Business account verification process
   - Message template creation and approval workflow (Bengali templates)
   - Webhook format for incoming messages
   - Media message handling (photos, documents)
   - Rate limits and pricing

6. **Bangladesh SMS Gateways (MuthoSMS / GreenWeb)**
   - API endpoint, authentication method (API key)
   - Single SMS and bulk SMS formats
   - Unicode Bengali SMS handling (character limits, encoding)
   - Delivery report (DLR) callback format
   - BTRC sender ID registration ("1000FIX")

7. **Firebase Cloud Messaging (FCM)**
   - Flutter integration: `firebase_messaging` package setup
   - Topic-based push for role-specific notifications vs device token push
   - Notification vs data message types
   - Background message handling on Android/iOS

8. **Traccar GPS Tracking (CD-13)**
   - Device registration API
   - Position reporting protocol (OsmAnd protocol from Flutter app)
   - WebSocket connection for real-time tracking on dispatch dashboard
   - Geofence API for zone-based alerts
   - Historical route playback API

9. **Brand Partner Warranty APIs (CD-04, CD-09)**
   - Samsung, Dell, HP, LG, Walton — warranty verification endpoints
   - Claim submission formats per brand (if APIs exist; manual portal process if not)
   - Authentication and rate limits per brand
   - Fallback: cached warranty data with manual verification override

10. **Biometric Attendance Integration**
    - Device models supported (ZKTeco, Suprema, or similar)
    - API/SDK for attendance data pull
    - Data format: employee ID, timestamp, in/out type
    - Polling frequency and sync mechanism to Odoo HR

11. **Sandbox Account Procurement Checklist**
    - Step-by-step process to obtain test credentials for each service
    - Expected lead times (bKash sandbox: 1–2 weeks, WhatsApp: 2–4 weeks)
    - Fallback mock services for development while awaiting credentials

**Cross-References:**
- Tech Stack Spec, Section 6.1–6.10 (All integration tool descriptions)
- BRD, Section 15 (Integration requirements and constraints)
- Implementation Strategy, Section 5 (Layer 3: Free Third-Party tools listing)

---

### Document 10: Flutter Mobile App Technical Architecture (CD-01)

**Priority:** P3 — Before Phase 2 (Month 5)
**Estimated Size:** 25–30 pages
**Audience:** Developer assigned to CD-01

**Why It Is Essential:**
CD-01 (Technician Mobile App) is the **single largest custom development item** at 16–20 person-weeks. It requires offline-first architecture with SQLite/Hive, GPS tracking, camera, barcode scanning, e-signature, Bengali UI, and background sync. This complexity demands its own architecture document.

**What It Must Contain:**

1. **Project Structure**
   - Feature-first vs layer-first organization — decision and rationale
   - Directory layout: `lib/features/`, `lib/core/`, `lib/shared/`
   - Dependency injection setup

2. **State Management**
   - Technology choice: Riverpod, BLoC, or Provider — decision with rationale
   - State architecture for offline-first (local-first, sync to server)
   - How UI reacts to connectivity changes

3. **Offline-First Architecture**
   - Local database: SQLite (via `drift`) or Hive — schema design
   - Which Odoo models are cached locally: jobs, customers, devices, parts catalog, checklists
   - Storage size estimates per technician (typical: 500 jobs history, 200 parts, 50 checklists)
   - Sync queue design: pending actions stored with timestamps, retry counts
   - Conflict resolution strategy: last-write-wins vs merge (decision and edge cases)
   - 24-hour offline guarantee verification

4. **Background Sync Service**
   - Connectivity detection (WiFi, 4G, 3G, 2G, offline)
   - Batch upload protocol: status updates first, then photos, then signatures
   - Partial sync recovery: what happens if sync is interrupted mid-batch
   - Battery optimization: sync frequency based on connectivity quality

5. **GPS & Location Services**
   - Traccar client protocol implementation (OsmAnd format)
   - Background location updates: Android foreground service, iOS significant location changes
   - Battery optimization strategies
   - GPS check-in validation (within 100m of customer address)

6. **Camera & Photo Handling**
   - Photo compression: max 200KB per image (per URD requirements)
   - EXIF metadata: GPS coordinates + timestamp stamped on photo
   - Upload queue: photos queued for upload, synced in background
   - Gallery view for existing job photos

7. **Barcode/QR Scanning**
   - Library: `mobile_scanner` or ZXing integration
   - Scan targets: device serial numbers, parts barcodes, job QR codes
   - Offline parts lookup against cached inventory data

8. **E-Signature Widget**
   - Canvas-based signature capture
   - Image encoding (PNG, base64)
   - Customer consent workflow

9. **Bengali Localization**
   - Flutter `intl` package setup with `arb` files
   - Bengali is LTR (no RTL handling needed)
   - Number formatting: Bengali numerals vs Western (configurable)
   - Font: Noto Sans Bengali bundled with app

10. **Push Notifications**
    - FCM setup for Android
    - Notification channels: Job Assignment, SLA Warning, System Update
    - Deep linking: notification tap → specific job detail screen
    - Background notification handling

11. **Authentication**
    - Keycloak OIDC PKCE flow for mobile
    - Token storage: Flutter Secure Storage
    - Token refresh flow and session expiry handling
    - Biometric login option (fingerprint)

12. **App Build & Release**
    - APK build process (Flutter build apk --release)
    - Internal distribution: Firebase App Distribution or direct APK
    - Version numbering aligned with ERP releases

**Cross-References:**
- Tech Stack Spec, Section 7.2 CD-01 (Mobile App module definition)
- URD, Journey Map 3 (Field Technician Daily Workflow)
- URD, User Stories US-FSM-001 through US-FSM-013
- BRD, Section 10 (Field Service Management requirements)

---

### Document 11: Testing Strategy & QA Plan

**Priority:** P3 — Week 4 (before Phase 1 coding ends)
**Estimated Size:** 15–20 pages
**Audience:** Both developers

**Why It Is Essential:**
With 2 developers and no dedicated QA engineer, testing must be built into the development workflow from the start. Odoo has its own testing framework (`odoo.tests`) that differs from standard Python unittest. Without a defined strategy, testing will be skipped under deadline pressure.

**What It Must Contain:**

1. **Odoo-Specific Testing Framework**
   - `TransactionCase`: for model method testing (auto-rollback)
   - `SavepointCase`: for read-heavy tests (faster, uses savepoints)
   - `HttpCase`: for controller/API endpoint testing
   - Test file location: `tests/test_*.py` in each custom module
   - Running tests: `./odoo-bin -c odoo.conf -d test_db --test-enable --stop-after-init -i module_name`

2. **Minimum Coverage Requirements**
   - Business logic methods: 80% coverage target
   - API controllers: 100% of endpoints tested
   - Computed fields: 100% tested (these are frequent bug sources in Odoo)
   - Security rules: 100% of `ir.rule` records tested with multi-user scenarios

3. **Test Data Fixtures**
   - YAML or Python-based test data for each module
   - Realistic Bangladesh data: Bengali names, phone numbers (+880 format), BDT amounts
   - Multi-branch test scenarios (Dhaka HQ + Sylhet branch + Chittagong branch)

4. **Integration Testing**
   - n8n workflow testing: trigger webhooks, verify downstream actions
   - Keycloak auth flow testing: login, token refresh, role-based access
   - Payment gateway testing: sandbox transaction end-to-end (bKash, SSLCOMMERZ)
   - SMS gateway testing: message delivery verification

5. **Flutter App Testing**
   - Unit tests: business logic, offline sync, data models
   - Widget tests: UI components, form validation
   - Integration tests: API calls against Odoo staging server
   - Offline scenario tests: complete 3 jobs offline, verify sync

6. **Manual UAT Test Scripts**
   - Tied to BRD acceptance criteria (Section 20)
   - One test script per user journey (12 journey maps from URD)
   - Role-based test scenarios: test as Agent, as Technician, as Manager

7. **Performance Testing**
   - Odoo load testing with Locust or similar
   - Targets from URD: 500 concurrent users, ≤3 sec page load (95th percentile)
   - Report generation: ≤5 sec for standard, ≤30 sec for 1000+ records
   - Database query performance benchmarks

8. **Bengali Text Testing**
   - Verify proper display, search, sorting of Bengali characters
   - SMS delivery with Bengali Unicode content
   - PDF generation with Bengali fonts (Mushak invoice, payslip)

**Cross-References:**
- BRD, Section 20 (Acceptance criteria for each module)
- URD, Section 16 (User Acceptance Criteria — portal-level UAT sign-off)
- URD, Section 12 (Performance standards — page load times, search response times)

---

### Document 12: Data Migration Runbook

**Priority:** P3 — Week 10 (before Phase 1 UAT)
**Estimated Size:** 15–20 pages
**Audience:** Team Leader (primary)

**Why It Is Essential:**
Phase 1 includes data migration of customers, devices, service history, and inventory data (Week 12–14 per Implementation Strategy). Legacy data exists in disconnected spreadsheets and standalone tools. Without a structured migration runbook, data quality issues will cascade into every module.

**What It Must Contain:**

1. **Source Data Inventory**
   - Catalog of all legacy data sources: Excel files, standalone databases, WhatsApp records
   - Data volumes per source (estimated: 250,000+ customer records, device records, service history)
   - Data quality assessment: completeness, accuracy, duplicates

2. **Field-by-Field Mapping**
   - Legacy columns → Odoo model.field for each entity:
     - Customers → `res.partner` (name, phone, address, NID)
     - Devices → `fieldservice.equipment` (serial, brand, model, purchase date, warranty end)
     - Service History → `fieldservice.order` / `helpdesk.ticket` (date, type, status, technician, resolution)
     - Inventory → `stock.quant` / `stock.lot` (part name, SKU, quantity, location, serial)
     - Employees → `hr.employee` (name, position, branch, certifications, join date)

3. **Data Cleansing Rules**
   - Duplicate detection: phone number matching, fuzzy name matching
   - Phone number normalization: various formats → +880XXXXXXXXXX
   - Address standardization: division/district/upazila hierarchy mapping
   - Date format unification: various formats → YYYY-MM-DD
   - Bengali text encoding verification (UTF-8)

4. **Migration Scripts**
   - Python scripts using Odoo `xmlrpc` or JSON-RPC API for bulk import
   - Batch size recommendations (500–1000 records per batch)
   - Error handling: log failures, continue processing, retry queue

5. **Migration Sequence (Dependency Order)**
   - Phase 1: Reference data (branches, service types, device categories, parts catalog)
   - Phase 2: Contacts (customers, vendors, brand partners)
   - Phase 3: Devices and warranty records
   - Phase 4: Service history and tickets
   - Phase 5: Inventory quantities

6. **Validation Queries**
   - Post-migration checks: record counts, referential integrity, sample verification
   - Business rule validation: warranty dates within range, phone number format, branch assignments

7. **Rollback Plan**
   - How to undo a failed migration batch
   - Database snapshot before each migration phase
   - Point-of-no-return identification

**Cross-References:**
- Implementation Strategy, Section 11.2 (Phase 1 Week 12–14: data migration milestones)
- BRD, Section 7 (Current state data landscape)
- Tech Stack Spec, Section 8 (Data model references)

---

### Document 13: Deployment & DevOps Pipeline

**Priority:** P3 — Week 3 (before first staging deployment)
**Estimated Size:** 15–20 pages
**Audience:** Team Leader (primary)

**Why It Is Essential:**
The Implementation Strategy shows a Docker/K3s deployment architecture but provides no CI/CD pipeline, staging environment configuration, or deployment procedures. Without this, developers deploy manually — which is error-prone and not reproducible.

**What It Must Contain:**

1. **Docker Configuration**
   - `Dockerfile` for Odoo 19 CE with custom modules
   - `docker-compose.dev.yml` for local development (all services)
   - `docker-compose.staging.yml` for staging environment
   - `docker-compose.prod.yml` for production (or K3s manifests)
   - Volume mounts for persistent data (PostgreSQL, filestore)

2. **CI/CD Pipeline (GitHub Actions or GitLab CI)**
   - Trigger: push to `develop` → run lint + test
   - Trigger: merge to `staging` → build Docker image, deploy to staging
   - Trigger: merge to `main` → build, deploy to production
   - Pipeline stages: lint (pylint-odoo) → test (odoo test runner) → build (Docker) → deploy
   - Test database provisioning for CI

3. **Staging Environment**
   - How to provision (VPS, cloud VM, or local server)
   - How to seed with test data (migration scripts + fixtures)
   - How to reset staging to clean state
   - URL and access management

4. **Production Deployment**
   - Zero-downtime Odoo module update procedure
   - Database backup before every deployment
   - Nginx reverse proxy configuration with SSL (Let's Encrypt)
   - Static asset serving optimization

5. **Database Operations**
   - Automated daily backup (PostgreSQL `pg_dump`)
   - Backup verification (automated restore test weekly)
   - Point-in-time recovery configuration
   - Database maintenance (VACUUM, REINDEX schedules)

6. **Monitoring & Alerting**
   - Grafana dashboards: Odoo worker health, PostgreSQL metrics, disk/memory usage
   - Log aggregation: Odoo log files → centralized logging
   - Alert thresholds: CPU >80%, disk >85%, response time >5sec, error rate >1%
   - Uptime monitoring for all services

7. **Secret Management**
   - No secrets in Git (`.env` in `.gitignore`)
   - Secrets storage: environment variables, Docker secrets, or Vault
   - Rotation policy for API keys and database passwords

**Cross-References:**
- Implementation Strategy, Section 9.3 (Docker deployment architecture diagrams)
- Tech Stack Spec, Section 6.11 (Tool version matrix for Docker images)
- Tech Stack Spec, Section 10 (Infrastructure requirements)

---

### Document 14: n8n Workflow Specifications

**Priority:** P3 — Week 8 (before notification workflows needed)
**Estimated Size:** 20–25 pages
**Audience:** Both developers

**Why It Is Essential:**
n8n is the workflow automation engine handling all notifications (SMS, email, WhatsApp, push), SLA escalations, payment reminders, renewal alerts, report generation, and inter-system orchestration. The Tech Stack lists n8n's role but does not define individual workflow specifications. Without this, developers will implement ad-hoc notification logic inside Odoo instead of using n8n — creating unmaintainable spaghetti.

**What It Must Contain:**

1. **Workflow Inventory**
   - Complete list of all n8n workflows with trigger conditions, actions, and schedule
   - Workflow naming convention: `WF-001-service-order-sms`, `WF-002-sla-breach-alert`

2. **Phase 1 Workflows (Core Operations)**
   - WF-001: New service order → SMS to customer (Bengali template)
   - WF-002: SLA breach warning → push notification to dispatch manager (T-60 min)
   - WF-003: SLA breach occurred → email to operations manager + push to branch manager
   - WF-004: Technician dispatched → SMS + WhatsApp to customer with technician name and ETA
   - WF-005: Job completed → SMS to customer with invoice link
   - WF-006: Daily operations summary → email to branch managers (8 PM daily)

3. **Phase 2 Workflows (Field Service)**
   - WF-007: Technician GPS check-in → SMS to customer ("technician has arrived")
   - WF-008: Parts request approved → push notification to technician
   - WF-009: Daily route optimization trigger → Timefold API call → push to technicians
   - WF-010: Technician not checked in by start time + 30 min → alert to dispatch

4. **Phase 3 Workflows (Finance)**
   - WF-011: Invoice generated → email + SMS with payment link
   - WF-012: Payment overdue (3/7/14 days) → escalating reminder SMS
   - WF-013: Monthly payroll processed → salary SMS to all employees

5. **Phase 4 Workflows (Contracts & Renewals)**
   - WF-014: AMC contract expiry → reminders at 60/30/15 days
   - WF-015: Warranty claim submitted → email to brand partner
   - WF-016: Warranty claim status change → notification to finance team

6. **Workflow Specification Template (Per Workflow)**
   - Trigger: webhook from Odoo / scheduled cron / manual
   - Input data: which Odoo fields/models are read
   - Processing logic: conditional routing, data transformation
   - Output actions: SMS (gateway + template), email (SMTP + template), push (FCM), WhatsApp
   - Error handling: retry count, fallback channel, dead letter queue
   - Bengali SMS templates (≤160 characters per message)

7. **n8n Credential Setup**
   - Odoo API credentials (service account)
   - SMS gateway API key
   - WhatsApp Business API token
   - Email SMTP configuration
   - FCM server key

8. **Testing Approach**
   - Sandbox mode: how to test workflows without sending real SMS/emails
   - Test phone numbers and email addresses
   - Workflow execution logs and debugging

**Cross-References:**
- URD, Section 14 (Notification & communication requirements — complete event-channel-language-timing matrix)
- BRD, Section 16 (Notification and alert requirements)
- Tech Stack Spec, Section 6.5 (n8n architecture and integration points)

---

### Document 15: Offline-First Sync Architecture

**Priority:** P3 — Before Phase 2 (Month 5)
**Estimated Size:** 15–20 pages
**Audience:** Developer assigned to CD-01

**Why It Is Essential:**
The Flutter technician app must work offline for 24 hours with guaranteed zero data loss on sync (UAT acceptance criteria). This is architecturally complex — conflict resolution, sync ordering, partial sync recovery — and needs careful design before coding. Getting this wrong means data loss in the field.

**What It Must Contain:**

1. **Local Database Schema**
   - Which Odoo models are cached locally and which fields
   - Tables: `jobs`, `customers`, `devices`, `parts_catalog`, `checklists`, `photos_queue`, `sync_queue`
   - Storage size estimates per technician (typical daily usage)

2. **Sync Protocol**
   - **Pull sync** (server → device): fetch assigned jobs, customer updates, parts catalog changes
   - **Push sync** (device → server): upload completed work, photos, signatures, GPS logs
   - Sync trigger: on connectivity restored, periodic (every 5 min when online), manual
   - Batch API endpoint design: single request to upload multiple changes

3. **Conflict Resolution**
   - Scenario: dispatch reassigns a job while technician is offline
   - Scenario: two technicians update the same parts inventory
   - Strategy: server-authoritative for assignments, client-authoritative for job documentation
   - Conflict notification: alert technician when sync reveals assignment changes

4. **Sync Ordering**
   - Priority 1: Status updates (Pending → In Progress → Complete)
   - Priority 2: Job documentation (diagnosis, repair notes, checklist)
   - Priority 3: Parts consumption records
   - Priority 4: Photos (largest payload, lowest urgency)
   - Priority 5: GPS breadcrumb trail

5. **Bandwidth Optimization**
   - Delta sync: only transfer changed records (using `write_date` from Odoo)
   - Photo compression: ≤200KB per image
   - Batch upload: group multiple changes into single API call
   - Adaptive quality: reduce sync frequency on 2G/3G

6. **Error Recovery**
   - Interrupted sync: resume from last successful item
   - Corrupted local database: re-download from server
   - Queue overflow: alert technician, prioritize critical data
   - Server error during sync: exponential backoff retry

7. **Sync Status UI**
   - Visual indicators: synced (green), pending (yellow), failed (red)
   - Last sync timestamp display
   - Manual sync button
   - Pending items count badge

8. **Acceptance Test Scenarios**
   - Complete 3 jobs offline over 4 hours
   - Reconnect and verify all data appears in Odoo within 30 seconds
   - Verify photo uploads complete within 2 minutes
   - Simulate conflict: server reassignment during offline period

**Cross-References:**
- URD, Section 13.7 (Offline & connectivity requirements — 24-hour offline, ≤200KB images)
- URD, User Story US-FSM-009 (24-hour offline operation with queue sync)
- Tech Stack Spec, Section 7.2 CD-01 (Mobile app offline architecture)

---

### Document 16: AI Dispatch Engine Algorithm Specification (CD-06)

**Priority:** P3 — Before Phase 2 (Month 5)
**Estimated Size:** 10–15 pages
**Audience:** Developer assigned to CD-06

**Why It Is Essential:**
CD-06 (AI Dispatch Engine) integrates VROOM/OSRM for Vehicle Routing Problem (VRP) optimization with Odoo scheduling. The algorithm needs formal specification — scoring weights, constraint definitions, optimization parameters — before a developer can implement it. Ad-hoc implementation will produce poor dispatch quality.

**What It Must Contain:**

1. **Input Data Model**
   - Technician attributes: location (lat/lng), skills (device types certified), current job queue, van parts inventory, work hours remaining
   - Job attributes: customer location, device type, estimated duration, priority level, SLA deadline, required skills
   - Constraints: max jobs per technician per day (7–8), zone restrictions, time windows

2. **Optimization Objective**
   - Primary: minimize total travel time across all technicians
   - Secondary: maximize skill match quality
   - Tertiary: balance workload across technicians
   - Override: emergency (P0) jobs bypass optimization — assign nearest qualified technician

3. **VROOM API Integration**
   - VRP input format: vehicles (technicians), jobs (service orders), shipments (if pick-and-drop)
   - VROOM API endpoint configuration (self-hosted VROOM instance)
   - Solution parsing: extract route sequence, travel times, unassigned jobs
   - Timeout handling: 5-second max for optimization response

4. **OSRM Integration**
   - Bangladesh road network data: OpenStreetMap extract, update frequency
   - Routing profile: car (for technician vans)
   - Distance matrix calculation for multi-technician, multi-job scenarios
   - Fallback: straight-line distance when OSRM is unavailable

5. **Scoring Formula**
   - Skill match score: exact match (1.0), partial match (0.5), no match (0.0)
   - Distance score: inverse of travel time (closer = higher score)
   - Workload balance: penalize technicians with >6 jobs, bonus for <4 jobs
   - Customer priority: multiply score by priority weight (P0=5x, P1=3x, P2=1x)
   - Combined score = w1*skill + w2*distance + w3*workload + w4*priority
   - Configurable weights (stored in Odoo system parameters)

6. **Re-Optimization Triggers**
   - New P0 emergency job arrives
   - Technician reports sick / goes offline
   - Job takes significantly longer than estimated (>30 min over)
   - Customer cancellation mid-route

7. **Fallback Strategy**
   - When VROOM/OSRM unavailable: simple nearest-qualified-technician assignment
   - When optimization fails: present manual dispatch board (current baseline)
   - Gradual rollout: AI suggests, dispatcher approves (Phase 2) → AI auto-assigns with override (Phase 3)

8. **Performance Targets**
   - Optimization response: ≤5 seconds for 200 technicians, 1000 jobs
   - Daily morning batch: ≤30 seconds for full-day optimization
   - Re-optimization: ≤3 seconds for single job insertion

**Cross-References:**
- Tech Stack Spec, Section 7.2 CD-06 (AI Dispatch Engine module definition)
- URD, Journey Map 4 (Dispatch Manager Morning Optimization — 9 min vs 45 min)
- URD, User Story US-SRM-007 (AI technician recommendation)
- BRD, Section 10 (Dispatch and scheduling requirements)

---

## 6. PRIORITY 4 — IMPORTANT REFERENCE DOCUMENTS

These documents are important but not blocking. They should be created alongside development.

---

### Document 17: Bengali Localization Implementation Guide

**Priority:** P4 — Ongoing (referenced across all phases)
**Estimated Size:** 10–15 pages
**Audience:** Both developers

**Why It Is Essential:**
Bengali localization appears in requirements across every module — UI labels, SMS messages, PDF reports (Mushak invoices), chatbot, mobile app. The URD specifies "100% UI translation with no English fallback" but does not explain HOW to implement this across Odoo, Flutter, and Next.js.

**What It Must Contain:**

1. **Odoo i18n Implementation**
   - `.po` file creation for all custom modules (`i18n/bn_BD.po`)
   - Translation process: extract → translate → compile
   - Translation management tool recommendation (Transifex, Weblate, or manual)
   - Bengali number formatting in Odoo (lakh/crore system: ৳1,23,456)

2. **PDF Report Templates**
   - Mushak 6.3 VAT invoice in Bengali — font embedding in QWeb/ReportLab
   - Service order printout, payslip, purchase order — all with Bengali headers
   - Font: SolaimanLipi or Noto Sans Bengali (must be embedded in PDF, not system-dependent)

3. **Flutter Localization**
   - `arb` files for Bengali (`app_bn.arb`)
   - Locale switching mechanism
   - Bengali date and number formatting
   - Bengali font bundling (ensure offline availability)

4. **SMS Templates**
   - Bengali text for each notification type (20+ templates from URD Section 14)
   - Character count management (Unicode Bengali: 70 chars = 1 SMS vs 160 for ASCII)
   - Template variables: `{customer_name}`, `{job_ref}`, `{eta}`, `{amount}`

5. **Database Considerations**
   - PostgreSQL collation: `bn_BD.UTF-8` or ICU collation for Bengali text sorting
   - Full-text search configuration for Bengali (if needed)
   - Bengali text indexing performance

6. **Translation Glossary**
   - Standardized Bengali translations for 50+ technical/business terms
   - Examples: Service Order = সার্ভিস অর্ডার, Invoice = চালান, Warranty = ওয়ারেন্টি, Technician = প্রযুক্তিবিদ
   - Consistent terminology across all platforms (Odoo, Flutter, SMS, WhatsApp)

**Cross-References:**
- URD, Section 13 (Localization requirements — Bengali primary, English secondary)
- URD, Section 14 (SMS templates — language and character constraints)
- BRD, Section 18 (Localization and compliance requirements)

---

### Document 18: OCA Module v19 Compatibility Verification Report

**Priority:** P4 — Week 1
**Estimated Size:** 10–15 pages
**Audience:** Team Leader

**Why It Is Essential:**
The Implementation Strategy assumes 94+ OCA modules are available for Odoo v19. However, OCA modules often lag behind Odoo releases by 3–6 months. Developers need a verified list of which OCA modules actually have a `19.0` branch, which need porting, and which have critical bugs.

**What It Must Contain:**

1. **Verification Matrix for All 94+ OCA Modules**
   - For each module: repository name, module name, v19 branch existence (yes/no)
   - Last commit date on v19 branch
   - CI status (passing/failing)
   - Known issues or migration notes

2. **Critical Modules Assessment**
   - `field-service` (33 modules): availability, maturity for v19
   - `helpdesk` (28 modules): availability, maturity for v19
   - `management-system` (33 modules): availability, maturity for v19
   - `operating-unit`: v19 readiness (critical for multi-branch)
   - `payroll`: v19 readiness (critical for HR module)

3. **Risk Assessment**
   - Modules with no v19 branch: porting effort estimate (hours per module)
   - Modules with failing CI: investigation needed
   - Alternative modules if primary choice unavailable

4. **Recommendations**
   - Which modules to install immediately
   - Which modules need porting work before use
   - Which modules should be replaced with custom development

**Cross-References:**
- Implementation Strategy, Section 5.2 (OCA module listing — 94+ modules across repositories)
- Tech Stack Spec, Section 4 (OCA module dependency matrix)

---

### Document 19: Operational Runbook & Monitoring Guide

**Priority:** P4 — Before Phase 1 go-live
**Estimated Size:** 15–20 pages
**Audience:** Team Leader (becomes ops support post-launch)

**Why It Is Essential:**
Once Phase 1 goes live, the 2-developer team becomes the support team. They need documented procedures for common operational tasks, troubleshooting, and incident response. Without this, production issues will be resolved through trial-and-error under pressure.

**What It Must Contain:**

1. **System Health Checks**
   - Odoo worker status verification
   - PostgreSQL connection pool monitoring
   - Redis cache status
   - Keycloak service health
   - n8n workflow execution status
   - Traccar device connectivity status

2. **Common Issue Resolution**
   - Odoo worker crash/restart procedure
   - Database connection exhaustion troubleshooting
   - n8n workflow failure investigation
   - SMS delivery failure debugging
   - Payment gateway timeout handling

3. **Database Operations**
   - Manual backup execution
   - Backup restoration procedure (tested)
   - Database upgrade after Odoo module update
   - Slow query identification and optimization

4. **User Management**
   - Creating new user accounts (Keycloak + Odoo)
   - Password reset procedure
   - Role/permission changes
   - Deactivating departing employees

5. **Incident Response**
   - Severity levels: P0 (system down), P1 (major feature broken), P2 (minor issue)
   - Escalation matrix (who to contact for what)
   - Communication templates for stakeholders during outages
   - Post-incident review template

6. **Scheduled Maintenance**
   - Weekly: database vacuum, backup verification, log rotation
   - Monthly: security patches, dependency updates, performance review
   - Quarterly: disaster recovery test, security audit

**Cross-References:**
- Tech Stack Spec, Section 10 (Infrastructure requirements)
- Implementation Strategy, Section 12 (Post-deployment support plan)
- BRD, Section 19 (SLA and availability requirements)

---

## 7. Document Creation Roadmap

| Week | Documents to Create | Owner |
|------|---------------------|-------|
| **Week 0 (Pre-Development)** | Doc 1: Dev Environment Setup | Team Leader |
| | Doc 2: Module Architecture | Team Leader |
| | Doc 4: Git Workflow & Standards | Team Leader |
| **Week 1** | Doc 3: Database Schema & Data Model | Both Developers (collaborative) |
| | Doc 5: Sprint Planning (2-person) | Team Leader |
| | Doc 18: OCA v19 Compatibility Report | Developer B |
| **Week 2** | Doc 6: API Specification | Both Developers |
| | Doc 7: Keycloak SSO Guide | Team Leader |
| | Doc 8: UI/UX Design System | Developer B |
| **Week 3** | Doc 13: Deployment & DevOps Pipeline | Team Leader |
| **Week 4** | Doc 11: Testing Strategy | Both Developers |
| **Week 8** | Doc 14: n8n Workflow Specifications | Developer B |
| **Week 10** | Doc 12: Data Migration Runbook | Team Leader |
| **Before Phase 2 (Month 5)** | Doc 9: Integration Technical Specs | Both Developers |
| | Doc 10: Flutter Mobile App Architecture | Developer assigned to CD-01 |
| | Doc 15: Offline Sync Architecture | Developer assigned to CD-01 |
| | Doc 16: AI Dispatch Algorithm Spec | Developer assigned to CD-06 |
| **Ongoing** | Doc 17: Bengali Localization Guide | Both Developers |
| **Before Go-Live** | Doc 19: Operational Runbook | Team Leader |

---

## 8. Critical Architectural Decision Required Before Day 1

> **Team Size vs. Timeline Mismatch**
>
> The existing Implementation Strategy and Technology Stack Specification assume a **6-person team** (2 senior Odoo developers, 2 Flutter developers, 1 DevOps engineer, 1 BA/QA). The actual UniSoft team is **2 full-stack developers**.
>
> This means the 18-month timeline is likely insufficient. Document #5 (Sprint Planning) must address this with one of three options:
>
> **(a)** Extend timeline to 24–30 months with 2 developers
> **(b)** Narrow Phase 1 scope — defer lower-priority modules (Privilege Program, Walk-in Queue Display, Bengali Chatbot) to later phases
> **(c)** Plan to add a third developer mid-project specifically for the Flutter mobile app (CD-01 alone is 16–20 person-weeks)
>
> **This decision must be made and documented before development begins.**

---

## 9. Summary

| Category | Count | Est. Pages |
|----------|-------|-----------|
| P1 — Blocking (Before Day 1) | 5 | 105–150 |
| P2 — Critical (Sprint 1) | 3 | 70–95 |
| P3 — Phase-Specific | 8 | 145–190 |
| P4 — Important (Ongoing) | 3 | 35–50 |
| **TOTAL** | **19** | **355–485** |

These 19 documents bridge the gap between the existing strategic/business documents and the hands-on technical guidance that UniSoft's 2-person development team needs to confidently begin and sustain implementation of the 1000FiX ERP system.

---

**Document End**
**Prepared by:** AI-Assisted Analysis
**Date:** March 18, 2026
**Next Action:** Prioritize and begin creating P1 documents (Documents 1–5) immediately.
