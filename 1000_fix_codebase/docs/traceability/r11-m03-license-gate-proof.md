# Annual Open-Source Licence Review & D-030 Gate Proof (R11-M03-T04)

**Document ID**: `LIC-ANNUAL-2026-R11`  
**Governing Decision**: `D-030` (Annual Open-Source Licence Review & Restricted Licence Policy)  
**Standard**: OpenChain (ISO/IEC 5230:2020) · CycloneDX 1.5 Specification  
**Evaluation Date**: 2026-10-22T14:34:44.083198+00:00  
**Status**: **`INCOMPLETE`** — licence gate exit 0, register audit APPROVED  

---

## 1. Executive Summary

Milestone **R11-M03-T04** executes the mandatory annual review of the `tooling/licence/register.yaml` open-source licence classification register. As established in architectural rule `D-030`, the licence register is **an ongoing operational governance control subject to annual re-certification**, not a one-off sign-off.

The SBOM is derived from the repository's dependency manifests (`uv.lock`, every `package-lock.json`, the `infra/` compose images, register components loaded as Postgres extensions); the pipeline gate classified it against the register. Each register condition was checked against the deployment manifests and the first-party sources that load the component. NOT_DEPLOYED rows (condition not triggered - nothing deploys or loads the component) are listed for review and do not block; a deployed component whose condition no static probe can observe is UNMEASURED and keeps the verdict from PASS, as does any component without a licence on record.

| Metric | Target | Actual Result | Status |
|---|---|---|:---:|
| **Dependencies with a Licence on Record** | 100% | **153/177 components (24 unclassified)** | **FAIL** |
| **Unapproved Restricted Licences** | **0** | **0** | **PASS** |
| **D-030 Condition Compliance** | 100% | **6/7 compliant (0 non-compliant, 1 not deployed, 0 unmeasured)** | **PASS** |
| **Four D-030 Replaced Components** | Retained | **4/4 verified retained** | **PASS** |
| **Licence Gate Pipeline Result** | Exit 0 | **Exit Code 0** | **PASS** |

---

## 2. Status of Four D-030 Replaced Components

1. **ceph** (register: approved): retained - deployed in infra/compose/docker-compose.yml:object-store
2. **apache/superset** (register: approved): retained - deployed in infra/compose/docker-compose.superset.yml:superset
3. **apache/airflow** (register: approved): retained - deployed in infra/compose/docker-compose.yml:airflow
4. **apache/kafka** (register: approved): retained - deployed in infra/compose/docker-compose.asset-ml.yml:kafka-1, infra/compose/docker-compose.asset-ml.yml:kafka-2, infra/compose/docker-compose.asset-ml.yml:kafka-3

---

## 3. Audit of Restricted-Licence Components with Conditions

7 register components carry a condition or a not-approved status:
- `grafana` (`AGPL-3.0-and-later`, register: approved-with-condition): **COMPLIANT** - every published port binds loopback only
- `loki` (`AGPL-3.0-and-later`, register: approved-with-condition): **COMPLIANT** - every published port binds loopback only
- `tempo` (`AGPL-3.0-and-later`, register: approved-with-condition): **COMPLIANT** - every published port binds loopback only
- `rustdesk` (`AGPL-3.0-and-later`, register: approved-with-condition): **NOT_DEPLOYED** - no infra/ manifest deploys it and no first-party source loads it
- `timescaledb` (`Apache-2.0/TSL dual`, register: approved-with-condition): **COMPLIANT** - no Timescale-enabled Postgres is deployed in infra/; the extension SQL refuses any server whose timescaledb.license is not 'apache' (migrations/sql/timescaledb_telemetry_hypertable.sql); no first-party SQL/Python calls a TSL-only feature
- `hashicorp/vault` (`BUSL-1.1`, register: not-approved): **COMPLIANT** - no infra/ manifest deploys it
- `redis` (`BSD-3-Clause (<=7.2 only)`, register: approved-with-condition): **COMPLIANT** - every image tag is 7.2.x

### Components without a licence on record (24)

- ast-serialize@0.13.1 (uv.lock)
- boolean-py@5.0 (uv.lock)
- cachecontrol@0.14.4 (uv.lock)
- cyclonedx-python-lib@11.12.0 (uv.lock)
- defusedxml@0.7.1 (uv.lock)
- librt@0.16.0 (uv.lock)
- license-expression@30.4.4 (uv.lock)
- markdown-it-py@4.2.0 (uv.lock)
- mdurl@0.1.2 (uv.lock)
- msgpack@1.2.3 (uv.lock)
- mypy@2.4.0 (uv.lock)
- mypy-extensions@1.1.0 (uv.lock)
- packageurl-python@0.17.6 (uv.lock)
- pathspec@1.1.1 (uv.lock)
- pip-api@0.0.35 (uv.lock)
- pip-audit@2.10.1 (uv.lock)
- pip-requirements-parser@32.0.1 (uv.lock)
- py-serializable@2.1.0 (uv.lock)
- rich@15.0.0 (uv.lock)
- sortedcontainers@2.4.0 (uv.lock)
- tomli@2.5.0 (uv.lock)
- tomli-w@1.2.0 (uv.lock)
- axllent/mailpit@v1.22 (infra/compose/docker-compose.yml:mailpit)
- mongo@7.0.14 (infra/compose/docker-compose.yml:novu-mongo)

---

## 4. Pipeline Gate Output Log

```
licence-gate: OK   grafana [AGPL-3.0-and-later] approved - condition: internal operational monitoring only; never a multi-tenant offering
licence-gate: OK   loki [AGPL-3.0-and-later] approved - condition: behind the trust boundary; no third-party log service
licence-gate: OK   tempo [AGPL-3.0-and-later] approved - condition: same class as Loki
licence-gate: OK   timescaledb [Apache-2.0/TSL dual] approved - condition: Apache-2.0-licensed features ONLY; TSL features must never be enabled (gate-tested)
licence-gate: OK - 177 dependencies classified, 0 unapproved restricted components
```

---

## 5. Certification Sign-off

Signed by:
- **Chief Technology Officer (CTO)**: *1000FiX Services Ltd.*
- **Chief Architect**: *Architecture Review Board (ARB) Lead*
- **Legal Counsel**: *Intellectual Property & Open-Source Compliance*
