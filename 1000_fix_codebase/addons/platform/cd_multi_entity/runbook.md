# Operational Runbook: 1000FiX Multi-Entity & Inter-Company Management (cd_multi_entity)

**Document**: `addons/platform/cd_multi_entity/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `M65` | **CD ID**: `CD-M65-03` | **Wave**: `W9`  
**Category**: `Platform/Administration` | **Layer**: `L3 Platform Consolidation`  
**Owner Squad**: `Platform & Finance Core`  
**Version**: `19.0.1.0.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_multi_entity` module (1000FiX Multi-Entity, Multi-Country & Consolidation) provides group financial consolidation, inter-company commercial rules, Bangladesh reference data pack instantiation, and statutory nil-return automation.

### 1.1 Business Scope
- **Multi-Company Consolidation (`fix.consolidation.book`)**: Periodic roll-up of subsidiary financial ledger balances into consolidated accounts with currency translation.
- **Inter-Company Elimination (`fix.elimination.entry`)**: Automated offset and elimination of internal revenue/expense, loan interest, and management fee transactions.
- **Inter-Company Trading Rules (`fix.intercompany.rule`)**: Transfer pricing markup rules complying with NBR Income Tax Act 2023 §107 arm's-length standards.
- **Inter-Company Transaction Reconciliation (`fix.intercompany.transaction`)**: Auto-mirror generation for counterparty bills and double-entry reconciliation.
- **Statutory Tax Calendar Localisation**: 15th-day Mushak return due date calculation with automated Bangladesh weekend (Friday/Saturday) and public holiday rollover.
- **Nil-Return Automation (`fix.nil.return.generator`)**: Automated zero-liability Mushak 9.1 and TDS Nil return generation for newly registered entities (§0.7.4 item 2).
- **Bangladesh Country Pack (`fix.country.pack.data.loader`)**: Concretely populates M30's `fix.country.pack` interface with 8 divisions, 64 districts, and public holidays.

### 1.2 Module Topology & Dependencies
- `base`: Core Odoo framework
- `mail`: Enterprise chatter and tracking audit trail
- `operating_unit`: OCA operating unit multi-branch boundary
- `cd_entity_config` (`M30`): Base legal entity, branch, and country pack interface
- **Isolation Invariant**: M51 (`cd_tax_engine_bd`) consumes M30's `fix.country.pack` interface directly and never depends on M65 (`cd_multi_entity`), preventing circular dependencies.

---

## 2. Standard Operating Procedures (SOPs)

### SOP-01: Running Month-End Group Consolidation
1. Navigate to **Administration > Consolidation > Consolidation Books**.
2. Select or create the consolidation period (e.g. `CONS-2026-M06`).
3. Verify member entity selection and target reporting currency (BDT).
4. Click **Run Consolidation** (`action_run_consolidation`) to aggregate subsidiary ledger lines.
5. Click **Generate Eliminations** (`action_generate_eliminations`) to offset inter-company transactions.
6. Verify net consolidated profit equals subsidiary revenue minus subsidiary expense minus inter-company eliminations.
7. Click **Close Consolidation** (`action_close`).

### SOP-02: Generating Statutory Nil-Returns for New Entities
1. Navigate to **Administration > Localisation > Nil-Return Declarations**.
2. Create declaration record selecting the target entity and tax period.
3. Click **Verify Eligibility** — system verifies zero transaction count and registration date.
4. Click **Generate Nil Packs** — system creates zero-liability Mushak 9.1 and TDS Nil JSON payloads.
5. Click **Submit to NBR** — system issues filing reference `NBR-ACK-<ENTITY>-<PERIOD>-NIL`.

---

## 3. Disaster Recovery & Rollback
- Reversibility: Consolidation books are non-destructive and can be reset to `draft` for re-calculation prior to closure.
- Statutory Audit Trail: All nil-return JSON payloads and inter-company matching timestamps are immutably archived for 5 years per NFR-095.
