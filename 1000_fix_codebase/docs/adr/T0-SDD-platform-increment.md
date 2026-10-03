# T0 Software Design Description — M28 + M29 + M30 as One Co-Designed Increment

**Task `P03-M01-T02`** · SDD standard: `AR-003` · Scope: three modules, one
boundary, one increment · Status: **issued** (Design Authority approval at `G1a`)

## 1. Why one SDD for three modules

`AR-006` §4.1 classifies `M28↔M29`, `M28↔M30`, `M29↔M30` as **legitimate
platform co-design pairs** — not defects. The gateway needs identity; identity
publishes through the gateway; configuration and integration are mutually
bootstrapping. This SDD treats the three as **one increment with three
deliverable units** (`CD-M28-*`, `CD-M29-*`, `CD-M30-*`), sharing a boundary
specification and a single install-order contract.

## 2. The shared boundary — what each module owns and what it consumes

```
┌─────────────────────────────────────────────────────────────────┐
│                      T0 Platform Increment                       │
│                                                                  │
│  ┌──────────┐  OIDC tokens  ┌──────────┐  routes   ┌─────────┐ │
│  │  M28 IPF │◄─────────────│  M29 SEC │◄──────────│ M30 ADM │ │
│  │ gateway   │              │ identity  │           │ entity   │ │
│  │ outbox    │─────────────►│ roles     │──────────►│ branch   │ │
│  │ events    │  introspect  │ SoD       │  config   │ calendar │ │
│  └──────────┘              └──────────┘           └─────────┘ │
│       │                         │                        │     │
│       ▼                         ▼                        ▼     │
│  cd_event_outbox          cd_rbac_ext              cd_entity_  │
│  (transactional)          (field-level)             config     │
└─────────────────────────────────────────────────────────────────┘
```

**The co-design contracts:**

| Contract | Owner | Consumer | Mechanism |
|---|---|---|---|
| Token introspection | `M29` | `M28` (Kong OIDC plugin) | OIDC `.well-known/openid-configuration` |
| Route registration | `M30` (config) | `M28` (Kong declarative) | Config-driven Kong YAML generation |
| Event publication | `M28` (outbox) | `M29`, `M30` + all domain modules | `cd_event_outbox` model, consumed by `fix_events` |
| Role assignment API | `M29` | `M21-core` (JML events) | Published REST API (sync one-way) |
| Feature flags | `M30` | All modules | `fix.feature.flag` model + `@flag_enabled` decorator |
| OU isolation | `M30` (`operating_unit_id`) | All transactional models | Record rules + `AS-03` |

## 3. The three cycles — why they are co-design

| Cycle | Resolution (per AR-006 §4.1 pairs 1–3) |
|---|---|
| `M28↔M29` | Kong needs Keycloak for introspection; Keycloak publishes its admin API through Kong. **Both are infrastructure, built together, one docker network, one compose profile.** |
| `M28↔M30` | Kong's routes are M30 configuration data; M30's configuration is served through Kong. **Config drives the gateway; the gateway serves the config API.** |
| `M29↔M30` | Roles are per-OU (M30's `operating_unit_id`); OUs are administered by role-holders (M29's RBAC). **Isolation tiers reference OUs; OU administration is role-gated.** |

## 4. Module decomposition (strict layer order `DL-01`…`DL-04`)

**Install order** (validated by `P03-M10-T01` clean-install proof):

```
1. base (Odoo 19 CE core)
2. OCA: operating-unit, server-tools/base_view_inheritance_extension
3. cd_entity_config (M30 — no platform deps)
4. cd_rbac_ext (M29 — depends cd_entity_config for OU isolation)
5. cd_event_outbox (M28 — depends cd_rbac_ext for publication auth)
```

**Layer discipline** (`FF-17`): `addons/platform/*` **never** depends on
`addons/domain/*`. The `depends` list in every platform manifest is:

```python
"depends": ["base", "operating_unit", "cd_entity_config"]  # example: cd_rbac_ext
```

## 5. Model contracts (the minimum each module delivers)

### `cd_entity_config` (M30) — owns: entity, branch, zone, calendar, flags

| Model | Key fields | Notes |
|---|---|---|
| `fix.entity` | `code`, `legal_name`, `company_id` | Extends `res.company`; one per legal entity |
| `fix.branch` | `entity_id`, `code`, `operating_unit_id`, `zone_id`, `address_id` | 51+ branches; the operational isolation unit |
| `fix.zone` | `code`, `name`, `geofence_ids` | Dispatch zone; consumed by M02 in Phase 5 |
| `fix.geofence` | `zone_id`, `polygon` (GeoJSON), `active` | Polygon or circle |
| `fix.working.calendar` | `branch_id`, `template_id`, `timezone` | M02's W2 availability stub calls this |
| `fix.feature.flag` | `key`, `enabled`, `scope` (global/branch/role) | `@flag_enabled` decorator reads this |
| `fix.bd.address` | `division_id`, `district_id`, `upazila_id`, `union_id` | 8/64/upazilas/unions reference data |

### `cd_rbac_ext` (M29) — owns: roles, isolation tiers, SoD, field rules

| Model | Key fields | Notes |
|---|---|---|
| `fix.role` | `code` (R-nn), `name`, `tier_ids`, `sod_group_id` | 53 roles per the reconciled register |
| `fix.isolation.tier` | `code` (T0…T5), `name`, `record_rule_domain` | The six data isolation tiers |
| `fix.sod.control` | `code`, `role_a_id`, `role_b_id`, `conflict_action` | 61 controls from `SP-006` |
| `fix.field.rule` | `model_id`, `field_id`, `role_ids`, `permission` (read/write/hidden) | The field-level permission engine |

### `cd_event_outbox` (M28) — owns: the transactional outbox

| Model | Key fields | Notes |
|---|---|---|
| `fix.event.outbox` | `event_type`, `payload` (JSONB), `aggregate`, `status` (pending/published/failed), `created_at` | Written in the **same transaction** as the business write (`AS-08`) |

## 6. Security architecture summary

- **53 roles** as Keycloak realm roles mapped to Odoo groups
- **Six isolation tiers** (`T0` public → `T5` residency-classified) as record rules with negative tests per role
- **61 SoD controls** — role-pair conflicts that block assignment
- **Field-level permissions** via `cd_rbac_ext` — `security/<module>_field_rules.xml`
- **Z4 human access** requires step-up authentication (`NFR-065`) + per-read logging (`NFR-070`)

## 7. The fitness functions this increment enables

| FF | Check | Status |
|---|---|---|
| `FF-09` | Residency single-client (`libs/py/fix_residency` only) | **Blocking from first build** |
| `FF-03` | Vendor clean / no unauthorised fork | **Blocking** (already live) |
| `FF-17` | Layer discipline (platform never depends on domain) | **Blocking** |
| `FF-21` | `company_id` + `operating_unit_id` on transactional models | **Blocking** |
| `FF-06` | No cross-module table reads | **Blocking** |

## 8. Interface break: `M21↔M29` (`P03-M08-T08`)

- `M21-core` **emits** `employee.joined` / `employee.left` / `employee.role_changed` events
- `M29` **consumes** these events to provision/deprovision Keycloak accounts
- `M21-core` calls `M29`'s **published REST API** for role assignment (sync one-way)
- **Never** synchronous-both-ways — that is a distributed monolith
