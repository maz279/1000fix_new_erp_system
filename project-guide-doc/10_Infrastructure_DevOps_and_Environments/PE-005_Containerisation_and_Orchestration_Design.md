---
id: PE-005
title: Containerisation & Orchestration Design
category: 10 — Infrastructure, DevOps & Environments
code: PE
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
approver: CTO with Design Authority (constituted under GV-002)
standards_basis: >
  OCI Image and Runtime Specifications · Kubernetes 1.34 · K3s · NIST SP 800-190 ·
  CIS Kubernetes Benchmark · Twelve-Factor App §6, §8, §9 · SLSA build provenance
traces_to: >
  PGD-000 PE-005 · PE-001 §4 zones, §9 HA · PE-002 · PE-003 §10.1 image boundary ·
  PE-004 §6 artefacts, §8 deployment, PE-004-F-02 readiness contract ·
  02-05 §7 · Technology Stack §21.1, §21.3 · AR-013 · NFR-003, NFR-004, NFR-008
depends_on: PE-001 · PE-002 · PE-003 · PE-004 · AR-013 · BE-007
verified_on: 2026-08-19
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-19 01:15 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# PE-005 — Containerisation & Orchestration Design

### Category 10 · Code `PE` · OCI · Kubernetes 1.34 / K3s · NIST SP 800-190

---

> **What existed before this document, enumerated 2026-08-19 01:15 (+06):**
>
> | Measure | Count |
> |---|---:|
> | Files mentioning Kubernetes or K3s | **3** |
> | Files mentioning Docker | 9 |
> | **Dockerfiles, Helm charts, Kubernetes manifests, Compose files in the estate** | **0** |
> | Components requiring an orchestration home (Technology Stack §21.1) | **17 classes**, plus 16 domain services and 10 applications |
>
> **And the fact that changes the shape of the problem, verified 2026-08-19:** Kubernetes supports
> the **three most recent minor versions**, each receiving patches for about **14 months**.
> **Kubernetes 1.34's support ends on 27 October 2026** — roughly two months from this issue, and
> inside Wave 1. **A 36-month programme on a 14-month platform requires an upgrade roughly every
> four months, forever.** No document in the estate has accounted for that.

---

## 1. Purpose

This document specifies how the estate's workloads are packaged and run: the image standard and base
image policy, the registry's content rules, the orchestration platform and its topology, workload
placement against `PE-001`'s trust zones, resource limits and autoscaling, service discovery and
east-west security, the **readiness contract** `PE-004` assigned here, storage, and the version
lifecycle that a 14-month-support platform imposes on a 36-month programme.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **Image standard** — base images, layers, users, size, reproducibility |
| 2 | Base image policy and the **update treadmill** |
| 3 | Registry content rules and scanning |
| 4 | **The orchestration ruling** — K3s, full Kubernetes, or neither, per wave |
| 5 | **Cluster topology**, and its mapping to `PE-001`'s zones |
| 6 | Workload placement, node pools and isolation |
| 7 | **Resource requests, limits and the QoS consequence** |
| 8 | Autoscaling — and where it must not be used |
| 9 | Service discovery, east-west mTLS, network policy |
| 10 | **The readiness and liveness contract** (`PE-004-F-02`) |
| 11 | Storage — what may be in a container and what may not |
| 12 | **The version lifecycle** a 14-month platform imposes |
| 13 | Odoo in containers — the case that does not fit the model |
| 14 | Fitness functions `FF-137`…`FF-146` |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The network the cluster sits in | **`PE-001`** | Zones, subnets, security groups |
| Which environments exist | **`PE-002`** | |
| The IaC that creates the cluster | **`PE-003`** §5.2 `cluster/` | This document specifies what it creates |
| The pipeline that builds and deploys images | **`PE-004`** | §6 artefacts, §8 deployment strategy |
| Instance counts and node sizes | **`PE-006`** | This document fixes shape; `PE-006` fixes size |
| Observability agents and what they collect | **`PE-008`** | This document reserves their placement |
| Secret injection into containers | **`PE-009`** | §9.4 states the interface only |
| Technology selection | `02-05` §7, `AR-013` | Consumed, not re-decided — except §5's orchestration ruling, which `AR-013` never made |
| Dependency pinning, SBOM, licence register | `BE-007` | Applied to images here |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Platform engineers | The whole document |
| Every developer | §3's image standard and §10's readiness contract are obligations on their component |
| **`PE-006` author** | §7's resource model is the unit its sizing produces |
| **`PE-004`** | §10 answers `PE-004-F-02`; §3.6 is a build stage |
| Security Lead | §3.2, §4.2, §9.3 |
| CTO | §5's ruling and §12's treadmill are multi-year commitments |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Concept | Conformance | Departure and rationale |
|---|---|---|---|
| **OCI Image / Runtime Specifications** | Image format and runtime | §3 — every artefact is OCI-compliant | None |
| **Kubernetes 1.34** | Orchestration API | §5, §6 | **Version currency is the issue, not conformance** — §12 |
| **K3s** | Lightweight conformant distribution | §5.2 | K3s tracks upstream Kubernetes; §12's treadmill applies unchanged |
| **NIST SP 800-190** | Application container security | §3.2, §4.2, §9.3 | None |
| **CIS Kubernetes Benchmark** | Cluster hardening | §5.4, applied through `PE-003` modules | None |
| **Twelve-Factor App §6, §8, §9** | Stateless processes, concurrency, disposability | §7, §10, §11 | **Departure on §6 for Odoo** — §13 |
| **SLSA** | Build provenance | Inherited from `PE-004` §6.4 | None |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| Technology Stack §21.1 | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` | Seventeen component classes with sizing drivers |
| Ibid. §21.3 | | HA per tier; the four total-outage components |
| `02-05` §7, §8.1 | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` | Docker/K3s named; the compute sizing table |
| `PE-001` §4, §9 | `./PE-001_*.md` | Six trust zones; HA topology; `HB-02` immutable infrastructure |
| `PE-003` §10.1 | `./PE-003_*.md` | The image/resource boundary |
| `PE-004` §6, §8, **`PE-004-F-02`** | `./PE-004_*.md` | Artefact rules; deployment strategy; **the unassigned readiness contract** |
| `AR-013` §6 | `../02_Architecture_and_Design/AR-013_*.md` | Licence rules; the component radar |
| `BE-007` | `../07_Build_Engineering_and_Development_Standards/BE-007_*.md` | Pinning, SBOM, vulnerability response, base-image currency |
| `AR-010` | `../02_Architecture_and_Design/AR-010_*.md` | Offline sync — a workload with unusual state characteristics |

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | Disposition |
|---|---|---|
| `PGD-000` `PE-005` — *"`02-05` names Docker/K3s. Three files mention Kubernetes. Twelve+ open-source systems plus Odoo, portals and services need an orchestration design"* | `PGD-000` | **Closed as a design.** §5, §6 |
| **`PE-004-F-02`** — the readiness-check obligation `NFR-008` depends on is unassigned | `PE-004` §8.2 | **Closed.** §10 is the contract, and `FF-142` enforces it |
| `PE-001` `HB-02` — immutable infrastructure | `PE-001` | §3.1, §11.1 |
| `AR-013` `LW-01` — every AGPL/BSL component needs a named fallback | `AR-013` | §5.3 applies it to the orchestration platform |
| `BE-007` §5.4 — *"runtime container and infrastructure scanning: `PE-007`"* | `BE-007` | **`BE-007` cites the wrong document.** Runtime container scanning is **`PE-005`** §4.3; `PE-007` is backup and DR. Raised as **`PE-A-03`** |

---

## 3. The Image Standard

### 3.1 What an image is

| Property | Rule |
|---|---|
| **Immutable** | Built once, never modified (`PE-004` §6.1). A change is a new image |
| **Minimal** | Only what the process needs at runtime. Build tooling does not ship |
| **Non-root** | Runs as an unprivileged user with a fixed UID |
| **Configuration-free** | No environment-specific value baked in (`PE-002` `PA-01`) |
| **Traceable** | Labelled with source commit, build time, version and `INT`/`CD` identifier where applicable |
| **Reproducible** | The same commit and lock file produce a functionally identical image |

### 3.2 Rules

| # | Rule |
|---|---|
| **IM-01** | **Multi-stage builds.** Build dependencies never appear in the final layer |
| **IM-02** | **A pinned base image by digest**, never by tag. `latest` is forbidden; so is `3.12` — `FF-137` |
| **IM-03** | **Runs as non-root**, with a **read-only root filesystem** where the process permits, and writable paths declared explicitly |
| **IM-04** | **No secrets, ever** — not in a layer, not in an ENV, not in a build argument. A secret in a discarded layer is still in the image history |
| **IM-05** | **No SSH server, no shell-based init, no package manager left executable** in a production image |
| **IM-06** | **All capabilities dropped** by default; any addition is named and justified |
| **IM-07** | **A declared health endpoint** (§10) |
| **IM-08** | **Handles `SIGTERM`** and drains within the termination grace period (§10.4) |
| **IM-09** | Logs to **stdout/stderr as structured JSON** (Twelve-Factor §11, `PE-008`) |
| **IM-10** | Labelled with the OCI standard label set plus `1000fix.component`, `1000fix.cd-id` and `1000fix.data-class` |
| **IM-11** | **An SBOM is generated at build and attached** (`BE-007`, `PE-004` §6.4) |

### 3.3 Base image policy

> **`PE-005-D-01`. One base image family, curated by Platform Engineering, per language runtime.**

| Runtime | Base | Reason |
|---|---|---|
| Python (Odoo, domain services) | A **minimal, security-maintained** distribution base | Odoo's C extensions and system dependencies make a fully distroless base impractical — §13 |
| Node (Next.js portals) | Minimal base; **distroless runtime stage** where the build permits | The build stage needs a toolchain; the runtime stage does not |
| Go / Rust services | **Distroless or scratch** | Static binaries need nothing else |
| Third-party (PostgreSQL, Redis, Kong, Keycloak…) | **Upstream official images, pinned by digest**, re-published into the private registry | Rebuilding upstream images is a maintenance burden with no security gain, provided they are pinned and scanned |

| # | Rule |
|---|---|
| **BI-01** | **Every application image derives from a curated base.** An arbitrary base fails `FF-138` |
| **BI-02** | Base images are **rebuilt on the `BE-007` monthly cadence** and out of cycle for a critical CVE |
| **BI-03** | **A base rebuild triggers a rebuild of every dependent image** — otherwise the patch reaches nothing |
| **BI-04** | Third-party images are **re-published into the private registry**, so an upstream deletion or retag cannot break a deployment |
| **BI-05** | Base image provenance and licence are recorded in the `BE-007` register |

> **`BI-03` is the rule most often written and least often implemented.** A patched base that no
> dependent image rebuilds against is a patch that exists only in the registry. **`FF-139` measures
> the age of the base layer in every running image**, which is the only way to know.

### 3.4 Size and layering

| # | Rule |
|---|---|
| **SZ-01** | Layers ordered **least- to most-frequently changed**, so a code change invalidates one layer |
| **SZ-02** | Dependencies installed from a **lock file** in a dedicated layer (`BE-007`) |
| **SZ-03** | **A production image over 500 MB is reviewed** — not forbidden. Odoo legitimately exceeds it; a Go service does not |
| **SZ-04** | No build caches, no `.git`, no test fixtures in the final image |

### 3.5 The `local` exception

`PE-002` §5.1 places `local` on Docker Compose (`BE-001`). **Compose files are development tooling,
not deployment artefacts**, and they are the one place where a developer-friendly image with a shell
and a debugger is permitted. `FF-137`…`FF-141` do not apply to `local`, and **no `local` image is
ever pushed to the shared registry**.

### 3.6 Build stages in the pipeline

| Stage | Check | Blocks |
|---|---|:--:|
| Base image pinned by digest | `IM-02` | ✔ |
| Derives from a curated base | `BI-01` | ✔ |
| Runs as non-root; no added capabilities | `IM-03`, `IM-06` | ✔ |
| No secret in any layer or in image history | `IM-04` | ✔ |
| **Vulnerability scan** — high/critical block | `BE-007`, `SC-005` | ✔ |
| SBOM generated and attached | `IM-11` | ✔ |
| Labels present | `IM-10` | ✔ |
| Health endpoint declared | `IM-07` | ✔ |

---

## 4. The Registry

`PE-004` §6.3 governs the registry **as an artefact store**. This section governs **image content**.

| # | Rule |
|---|---|
| **RC-01** | **Scan on push, and re-scan on a schedule.** A clean image at build time is not clean in six months (`PE-004` `RG-04`) |
| **RC-02** | **A running image whose re-scan finds a critical vulnerability raises an incident**, on the `BE-007` response clock — not a ticket in a backlog |
| **RC-03** | **Images are immutable and tags are not moved.** Production pulls by digest (`PE-004` `RG-02`) |
| **RC-04** | Upstream third-party images are **mirrored on ingestion**, scanned, and pinned |
| **RC-05** | **`BD-R` has its own registry replica**, or a pull path over the §8.2 private link — a site that cannot pull an image cannot recover (`PE-007`) |

> **`PE-005-F-01`. `RC-05` is a `PE-007` dependency nobody has stated.** `BD-R` is a colocation
> facility in a different jurisdiction. **If its only image source is a regional registry reachable
> over the cross-border link, then a link failure makes the resident tier unrecoverable as well as
> unreachable** — which converts `SC-007` §9.2's *degraded* mode into an *outage*. Referred to
> `PE-007` §5.

---

## 5. Orchestration

### 5.1 What must run

Technology Stack §21.1 and `02-05` §8.1 between them require homes for:

| Class | Examples | Character |
|---|---|---|
| **Odoo** | 4 app nodes, 2 cron, 2 long-polling | **Stateful-adjacent** — §13 |
| Portals | 3 Next.js instances | Stateless |
| **Domain services** | 16 (`CD-233`…`248`) | Stateless |
| **Stateful stores** | PostgreSQL, TimescaleDB, ClickHouse, Redis, MinIO, Redpanda | **§5.5 — not in the cluster** |
| Platform services | Keycloak, Kong, n8n, Novu, Metabase, Grafana, Traccar, VROOM/OSRM, Mayan, Wazuh, MLflow | Mixed |
| ML inference | Ollama, optional GPU | Specialised |
| **`CD-233` residency service** | In **`BD-R`** | §6.4 |

### 5.2 The ruling

> **`PE-005-D-02`. K3s from Wave 1, on the same Kubernetes API, with a documented promotion path to
> a managed Kubernetes service if and when the operational load justifies it.**

| Option | Assessment |
|---|---|
| **No orchestration** — Compose or systemd on VMs | Fails `NFR-008`: rolling deployment, health-gated replacement and service discovery would all be hand-built. `PE-002` has **twelve** environments |
| **K3s** | ✅ **Chosen for W1.** Conformant Kubernetes API, single-binary, low operational overhead, runs identically in `BD-R` colocation where no managed service exists |
| Managed Kubernetes | Lower operational burden **where available** — and it is **not available in `BD-R`**. Same API, so this is a deployment-topology change, not a redesign |
| A PaaS | Would not host the stateful stores or the `BD-R` tier |

**The decisive argument is `BD-R`.** A managed Kubernetes service cannot be deployed into a
Bangladeshi colocation facility. **K3s can run in both places, on one API**, so the estate operates
one orchestration model rather than two.

### 5.3 Licence position

| Component | Licence | `AR-013` `LW-01` |
|---|---|---|
| Kubernetes | Apache-2.0 | Permissive — passes `A-01` |
| **K3s** | **Apache-2.0** | Permissive — passes `A-01` |
| Container runtime (containerd) | Apache-2.0 | Passes |

**No exception required**, which is the same test `PE-003` §4.2 applied to the IaC engine.

### 5.4 Cluster topology

| Environment | Clusters | Control plane | Rationale |
|---|---|---|---|
| `prod` | **1 regional** + **1 in `BD-R`** | HA — 3 control-plane nodes regionally; **2 with an external datastore in `BD-R`** | `Z4` is a different site and a different jurisdiction |
| `dr` | **1 regional standby** + **`BD-R` standby** | Minimal standing, **scaled from IaC on failover** (`PE-002` §5.12.1) | |
| `staging`, `migration-staging` | 1 each | HA control plane — **because they rehearse production** | |
| `uat`, `sit`, `perf`, `training`, `sandbox` | 1 each | Single control-plane node | Cost; a control-plane failure is an inconvenience |
| `dev`, `ci` | 1 shared, namespace-isolated | Single | `ci` workloads are ephemeral namespaces |
| `local` | None | — | Compose |

| # | Rule |
|---|---|
| **CL-01** | **CIS Kubernetes Benchmark** baseline, applied through `PE-003` modules |
| **CL-02** | The API server is **never internet-facing**. It is reachable from `Z5` only (`PE-001` `MA-02`) |
| **CL-03** | **Audit logging enabled** and shipped to `PE-008` |
| **CL-04** | **`BD-R`'s cluster is separately credentialled.** Regional cluster admin grants nothing there (`PE-001` `MA-04`) |
| **CL-05** | **No cluster spans a jurisdiction.** A single cluster with nodes in both sites would put `Z4` scheduling decisions in a regional control plane |

> **`CL-05` is a residency decision expressed as a topology rule.** A stretched cluster would mean
> the regional control plane holds metadata about `Z4` workloads and could, in principle, schedule a
> `Z4` pod regionally. **Two clusters make that structurally impossible**, which is the same
> reasoning as `PE-001` `NR-02`.

### 5.5 What does not run in the cluster

> **`PE-005-D-03`. Stateful data stores run outside the cluster.**

| Store | Where | Why |
|---|---|---|
| PostgreSQL (primary, replicas, **resident**) | Managed service or dedicated hosts | Backup, failover, PITR and version upgrades are better solved by the data tier than by an operator |
| TimescaleDB, ClickHouse | As above | |
| Redis | Managed or dedicated | |
| **Redpanda** | Dedicated (W6) | |
| MinIO | Dedicated | |

**Why not:** running the estate's primary database on Kubernetes adds an operator, its CRDs and its
failure modes between the data and its recovery. **`NFR-007`'s RPO ≤ 15 min and `PE-007`'s restore
path are simpler and more testable against a conventional data tier**, and this is a programme with
no existing Kubernetes operational experience to draw on.

**Consequence, stated:** two operational models — cluster workloads and data hosts. `PE-003` covers
both, and `PE-001` `HB-02`'s immutability applies to both.

---

## 6. Workload Placement

### 6.1 Node pools

| Pool | Zone | Workloads | Isolation |
|---|---|---|---|
| `app` | `Z2` | Odoo app, portals, domain services | Standard |
| `cron` | `Z2` | Odoo cron, scheduled jobs | **Tainted** — only cron workloads schedule here (§6.3) |
| `platform` | `Z2` | Keycloak, Kong, n8n, Novu, Grafana… | Standard |
| `ingress` | `Z1` | Kong, Nginx | **Public subnet**; nothing else schedules here |
| `ml` | `Z2` | Ollama, MLflow; optional GPU | Tainted; W6 |
| **`resident`** | **`Z4`, `BD-R` cluster** | **`CD-233` only** | **A separate cluster**, not a pool (§5.4) |

### 6.2 Zone conformance

| # | Rule |
|---|---|
| **WP-01** | **A workload's node pool determines its zone**, and the zone determines its network policy (`PE-001` §4.1) |
| **WP-02** | **No workload schedules in `Z1` except ingress.** `FF-140` |
| **WP-03** | **No regional workload schedules into the `BD-R` cluster**, and `CD-233` schedules nowhere else. `FF-141` |
| **WP-04** | Anti-affinity spreads replicas of an HA component **across nodes and availability zones** (`PE-001` `HA-01`) |

### 6.3 Why cron is tainted

`PE-004` §8.3 rules Odoo cron nodes **stopped, migrated and started** because two schedulers means
one job runs twice. **A tainted pool makes that enforceable:** cron pods cannot drift onto app nodes
during a rolling deployment, which would silently create the second scheduler the rule exists to
prevent.

### 6.4 `CD-233` placement

| # | Rule |
|---|---|
| **RP-01** | `CD-233` runs **only** in the `BD-R` cluster |
| **RP-02** | It is the **only** workload permitted to reach `Z4` storage (`PE-001` `NR-02`) |
| **RP-03** | It is HA — **at least two replicas** — because it gates every `T5` read |
| **RP-04** | Its image is pulled from the `BD-R` registry replica (`RC-05`) |

---

## 7. Resources

### 7.1 Requests and limits

| # | Rule |
|---|---|
| **RL-01** | **Every container declares CPU and memory requests and limits.** An unbounded container starves its neighbours — `FF-143` |
| **RL-02** | **Memory limit equals memory request** for every production workload, so every pod is `Guaranteed` QoS and is not evicted under node pressure |
| **RL-03** | **CPU limits are set but may exceed the request**, so a burst is permitted while the request guarantees a floor |
| **RL-04** | Values come from **`PE-006`'s measurements**, not from guesses — and `PE-006` derives them from `perf` runs |
| **RL-05** | **A workload OOM-killed twice in a week is a finding**, not a restart |

> **`RL-02` is the decision most often made by omission.** Leaving the memory limit above the
> request makes a pod `Burstable`, which means the scheduler may evict it under node memory
> pressure. **For Odoo application nodes serving 800 concurrent internal users, an eviction is a
> user-visible outage on a node that was working.**

### 7.2 Autoscaling

| Component | Horizontal autoscaling | Reason |
|---|---|---|
| Next.js portals | **Yes** | 75,000+ concurrent portal users (`NFR-004`); stateless; traffic is peaky |
| Domain services | **Yes** | Stateless |
| **Odoo application nodes** | **No — fixed count, scaled deliberately** | §7.3 |
| **Odoo cron** | **Never** | Two schedulers means duplicate jobs (`PE-004` §8.3) |
| Platform services | **No** | Sized for their function |
| ML inference | **No** | GPU-bound where present; scaling is a cost decision |

### 7.3 Why Odoo is not autoscaled

| # | Reason |
|---|---|
| **Worker model.** Odoo pre-forks a fixed worker count per node; the scaling unit is workers, and adding a node adds 12 at once |
| **Database connections.** Every worker holds connections. Autoscaling application nodes autoscales pressure on the PostgreSQL primary — **the tier that cannot scale horizontally** |
| **Warm-up.** A new Odoo node is slow until its registry and caches are warm, which interacts badly with the readiness contract (§10.2) |
| **Predictability.** Internal user load (`NFR-003`, 800 concurrent) is predictable; portal load is not |

> **`PE-005-F-02`. Autoscaling the application tier without a connection pooler in front of
> PostgreSQL converts a traffic spike into a database outage.** A pooler is not named in
> Technology Stack §21.1 and appears nowhere in `02-05` §8.1. **Referred to `PE-006` and `DA-001`
> as a required component**; `Q-03`.

### 7.4 Cluster capacity

| # | Rule |
|---|---|
| **CC-01** | Node pools carry **enough headroom to lose one node** without pending pods — otherwise `PE-001` `HA-01` is true on paper only |
| **CC-02** | **Pod disruption budgets** on every HA component, so a voluntary eviction cannot take the last replica |
| **CC-03** | Cluster autoscaling adds **nodes**, and it is bounded — an unbounded scaler is an unbounded bill |
| **CC-04** | Resource utilisation feeds `PE-006` and `PE-008` |

---

## 8. Service Discovery and East-West Security

| # | Rule |
|---|---|
| **SD-01** | Services are discovered by **cluster DNS name**, never by IP |
| **SD-02** | **Cross-cluster** discovery (regional ↔ `BD-R`) is by **explicit endpoint**, over the §8.2 private link — never by service mesh federation, which would blur `CL-05`'s boundary |
| **SD-03** | **East-west traffic uses mTLS with workload identity** (`PE-001` `SG-06`) |
| **SD-04** | **Network policy is default-deny per namespace.** A workload reaches only what it declares — `FF-144` |
| **SD-05** | **`PE-001`'s zone rules are enforced at the network-policy layer as well as at the subnet layer.** Two mechanisms, both must fail |
| **SD-06** | **All egress leaves through `Z6`** (`PE-001` `EG-01`); no pod has a direct route out |

> **`PE-005-D-04`. Network policy, not a service mesh, at Wave 1.** A mesh would add mTLS, traffic
> shifting and observability — and a control plane, a sidecar per pod, and an upgrade cycle, to a
> team with no Kubernetes operational history. **mTLS is achievable without a mesh; the rest is not
> required until traffic-shifted deployments are.** Reviewed at the W5 gate.

---

## 9. Container Security

| # | Rule |
|---|---|
| **CS-01** | **Non-root, read-only root filesystem, all capabilities dropped** (`IM-03`, `IM-06`) |
| **CS-02** | **No privileged containers.** An exception is an architecture decision with an expiry |
| **CS-03** | **No host network, no host PID, no host path mount** except for named observability agents (`PE-008`) |
| **CS-04** | Admission control **rejects** a workload violating `CS-01`…`CS-03` — `FF-145` |
| **CS-05** | **Only images from the private registry, by digest**, may be deployed (`PE-004` `RG-02`) |
| **CS-06** | Runtime detection (Wazuh, `INT-029`) on `Z4` and `Z5` **from W1**, elsewhere from W5 (`PE-001` `HB-05`) |
| **CS-07** | **Secrets are mounted from the secret manager at runtime** (`PE-009`), never baked, never in a plain Kubernetes Secret alone |

---

## 10. The Readiness Contract

**`PE-004-F-02`** records that condition 3 of zero-downtime deployment — *"health checks that mean
it"* — is a per-component design obligation **nobody had assigned**. It is assigned here.

### 10.1 Three distinct probes

| Probe | Answers | On failure |
|---|---|---|
| **Startup** | *"Has the process finished starting?"* | Restart, after a generous budget |
| **Readiness** | *"Can this instance serve traffic **right now**?"* | **Removed from the load balancer** — not restarted |
| **Liveness** | *"Is this process irrecoverably stuck?"* | **Restarted** |

### 10.2 The rules

| # | Rule |
|---|---|
| **RD-01** | **Every workload declares all three probes.** `FF-142` |
| **RD-02** | **Readiness returns healthy only when the instance can actually serve** — database connection acquired, required caches warm, dependent clients initialised. **Not when the process started** |
| **RD-03** | **Readiness must not depend on a downstream dependency's health.** A database blip must not mark every application node unready simultaneously, which turns a degraded dependency into a total outage |
| **RD-04** | **Liveness must be cheap and local.** A liveness probe that queries the database restarts every node when the database is slow — **the single most damaging probe mistake** |
| **RD-05** | **Startup budgets are generous and per-component.** Odoo registry loading takes far longer than a Go service starting |
| **RD-06** | Probe failures are **observable** (`PE-008`); a flapping readiness probe is a finding |

> **`RD-03` and `RD-04` are opposites of the intuitive design, and both cause outages.** The
> instinct is to make health checks thorough. **A thorough liveness probe turns a slow dependency
> into a restart storm; a dependency-aware readiness probe turns a partial outage into a total
> one.** The correct design is a shallow liveness probe and a readiness probe about *this instance
> only*.

### 10.3 Per-component budgets

| Component | Startup | Readiness period | Liveness |
|---|---|---|---|
| Odoo app | Generous — registry load | Short | Shallow, process-local |
| Odoo cron | Generous | n/a — takes no traffic | Shallow |
| Next.js portal | Short | Short | Shallow |
| Domain services | Short | Short | Shallow |
| `CD-233` | Short | Short — **and it gates every `T5` read**, so its readiness is measured separately (`PE-008`) | Shallow |

### 10.4 Termination

| # | Rule |
|---|---|
| **TR-01** | **`SIGTERM` starts a graceful shutdown**: stop accepting new work, finish in flight, close cleanly |
| **TR-02** | **Readiness fails first**, so traffic drains before the process stops (`PE-004` §8.2 condition 4) |
| **TR-03** | The **grace period exceeds the longest expected in-flight request** — otherwise a rolling deployment kills live requests |
| **TR-04** | **Event consumers commit their position before exiting** (`AR-009` `C-01`), so a redeployment does not replay |
| **TR-05** | **Cron jobs are not interrupted mid-run**; deployment waits or the job is idempotent — and `PE-004-F-03` records that estate-wide job idempotency is unspecified |

---

## 11. Storage

| # | Rule |
|---|---|
| **ST-01** | **Containers are ephemeral.** Anything written to a container filesystem is lost, deliberately |
| **ST-02** | Persistent data lives in the **data tier** (§5.5) or in **object storage** |
| **ST-03** | **File uploads go to object storage** (MinIO), never to a pod filesystem — `NFR-060`, and the claim-check pattern (`AR-009` P-05) |
| **ST-04** | **No `ReadWriteMany` volume for application state.** A shared filesystem between application replicas is shared mutable state with no locking discipline |
| **ST-05** | Ephemeral scratch space is **sized and limited**; a pod filling a node's disk is a node-wide outage |
| **ST-06** | **Malware scanning happens on upload, before storage or serving** (`NFR-063`) — an infrastructure service, not a per-module concern |

---

## 12. Version Lifecycle — The Treadmill

### 12.1 The fact

Verified **2026-08-19**:

| Fact | Position |
|---|---|
| Kubernetes supports the **three most recent minor versions** | 1.34, 1.35, 1.36 currently supported |
| Each minor receives patches for **about 14 months** | |
| **Kubernetes 1.34 support ends 27 October 2026** | **Inside Wave 1** |
| Minor releases arrive roughly every **4 months** | |
| **K3s tracks upstream** and maintains the corresponding release lines | |

### 12.2 What that means for a 36-month programme

> **`PE-005-F-03`. A 36-month programme on a platform with 14-month support requires roughly
> **nine** Kubernetes minor upgrades across its life, and one of them falls inside Wave 1.**
>
> No document in the estate has accounted for this. `AR-013` §7's currency table carries Odoo,
> PostgreSQL, Keycloak and OCA — **Kubernetes and K3s are not on it.** Technology Stack §17.4 sets
> operational standards for Keycloak, Odoo, OCA and PostgreSQL and **not for the orchestration
> platform**, which is the component with the shortest support window of all of them.

### 12.3 The policy

| # | Rule |
|---|---|
| **VL-01** | The cluster runs a version with **at least 6 months of remaining upstream support** |
| **VL-02** | **Upgrades are planned quarterly**, not reactively. An upgrade under EOL pressure is an upgrade without a rehearsal |
| **VL-03** | Upgrade order: `dev`/`ci` → `sit` → `staging` → **`prod`** → `dr`, with at least one wave-gate cycle in `staging` |
| **VL-04** | **`BD-R`'s cluster upgrades on the same cadence.** A resident tier two versions behind is an unrehearsed failover target |
| **VL-05** | **Kubernetes and K3s are added to `AR-013` §7's currency table** with a per-wave-gate review — `PE-A-04` |
| **VL-06** | Deprecated API usage is detected **before** an upgrade, in CI (`FF-146`) |

> **`VL-06` is what makes `VL-02` achievable.** Kubernetes upgrades break on removed APIs, and the
> manifests that use them are in the repository. **Detecting them in CI turns an upgrade from an
> investigation into a task.**

---

## 13. Odoo — The Case That Does Not Fit

`Twelve-Factor §6` asks for stateless processes. **Odoo is not one**, and pretending otherwise
produces a design that fails in production.

| Characteristic | Consequence |
|---|---|
| **Pre-forked workers**, fixed per node | The scaling unit is a node of 12 workers, not a pod (`§7.3`) |
| **A module registry loaded at startup** | Startup is slow; `RD-05`'s generous budget exists for this |
| **Filestore** for attachments | Must be object storage (`ST-03`), never a pod filesystem — otherwise attachments land on one replica |
| **Long-polling** needs sticky routing or a dedicated node set | Technology Stack §21.1 gives it 2 dedicated nodes |
| **Cron is a singleton concern** | `PE-004` §8.3; §6.3's taint |
| **Module upgrades are schema migrations** | `PE-004` `OD-03`, `ME-03` |

> **`PE-005-D-05`. Odoo runs in containers, orchestrated, but is treated as a
> *stateful-adjacent* workload**: fixed replica count, generous startup budget, dedicated cron and
> long-polling pools, object-storage filestore, and **no autoscaling**. **The container is a
> packaging and deployment mechanism for Odoo, not a scaling one.**

---

## 14. Fitness Functions

Allocation confirmed by enumerating every `FF-nn` definition across all authored categories at
**2026-08-19 01:15 (+06)**, per `PGD-AUDIT-007` `PGD-A7-01`.

| # | Check | Scope | Timing | Enforcement |
|---|---|---|---|---|
| **FF-137** | Every image pins its base **by digest**; no floating tag | All images | Build | **Fail** |
| **FF-138** | Every application image derives from a **curated base** | All | Build | **Fail** |
| **FF-139** | **No running image's base layer is older than the current base by more than one cadence** (`BI-03`) | Runtime | Weekly | **Fail** |
| **FF-140** | No workload schedules into the `Z1` ingress pool except ingress | Cluster | Runtime | **Fail** |
| **FF-141** | **No regional workload runs in the `BD-R` cluster**, and `CD-233` runs nowhere else | Both clusters | Runtime | **Fail** |
| **FF-142** | **Every workload declares startup, readiness and liveness probes**, and no liveness probe performs a network call to a dependency | All | CI on manifests | **Fail** |
| **FF-143** | Every container declares CPU and memory requests and limits; **production memory limit equals request** | All | CI + runtime | **Fail** |
| **FF-144** | Every namespace has a **default-deny** network policy | All | CI + runtime | **Fail** |
| **FF-145** | Admission control rejects privileged, host-network, host-PID and host-path workloads outside the named exceptions | All | Runtime | **Block** |
| **FF-146** | **No manifest uses a Kubernetes API deprecated in the next two minor versions** | All | CI | **Fail** |

---

## 15. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `PE-005-D-01` | Base images | Per-team choice · **curated family per runtime** · fully distroless everywhere | **Curated per runtime** | Distroless is right for static binaries and impractical for Odoo's system dependencies | `BI-01`…`BI-05`; `FF-138` |
| `PE-005-D-02` | Orchestration | None · **K3s** · managed Kubernetes · PaaS | **K3s** | It is the only conformant option that runs identically in regional cloud **and** in `BD-R` colocation, so the estate operates one model | §5.2; promotion path documented, not foreclosed |
| `PE-005-D-03` | Stateful stores | In-cluster with operators · **outside the cluster** | **Outside** | An operator between the primary database and its recovery adds failure modes to the path `NFR-007` depends on, in a programme with no Kubernetes operational history | §5.5; two operational models, both under `PE-003` |
| `PE-005-D-04` | Service mesh | Mesh at W1 · **network policy + mTLS, mesh reviewed at W5** | **No mesh at W1** | mTLS is achievable without a mesh; a mesh adds a control plane and an upgrade cycle to a team with no Kubernetes history | §8; reviewed at the W5 gate |
| `PE-005-D-05` | Odoo model | Stateless, autoscaled · **stateful-adjacent, fixed count** | **Stateful-adjacent** | Pre-forked workers, slow registry load, singleton cron and a filestore make it a packaging case, not a scaling one | §13; `§7.3` |
| `PE-005-D-06` | Cluster per jurisdiction | One stretched cluster · **two clusters** | **Two** | A stretched control plane holds `Z4` scheduling metadata and could schedule a `Z4` pod regionally | `CL-05`; `FF-141` |
| `PE-005-D-07` | Pod QoS | Burstable · **Guaranteed for production** | **Guaranteed** | Eviction of a working Odoo node under node pressure is a user-visible outage | `RL-02` |
| `PE-005-D-08` | Liveness probes | Thorough, dependency-aware · **shallow and process-local** | **Shallow** | A dependency-aware liveness probe restarts every node when the database is slow | `RD-04`; `FF-142` |

---

## 16. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Is `PE-005-D-02` ratified?** Every manifest, module and runbook is written against an orchestration platform | Design Authority + CTO | **W0 — blocking** | `PE-003` `cluster/`, `PE-004` deployment |
| **Q-02** | **Does `BD-R` support a K3s cluster and a registry replica?** (`RC-05`, `PE-005-F-01`) If not, the resident tier is unrecoverable on link failure | Platform Engineering Lead | **W1** | `PE-007`, `CD-233` |
| **Q-03** | **Is a PostgreSQL connection pooler in the design?** It is in no sizing table, and portal autoscaling without one converts a spike into a database outage (`PE-005-F-02`) | Chief Architect + `PE-006` | **W1** | `NFR-004`, autoscaling |
| **Q-04** | **Who owns the Kubernetes upgrade treadmill**, and is nine upgrades over 36 months in any plan? (`PE-005-F-03`) | Platform Engineering Lead + `GV-004` | **W1** | `VL-02`, every wave |
| **Q-05** | Does the estate accept **two operational models** — cluster and data hosts — or does the data tier move in later? | CTO | W2 | §5.5 |
| Q-06 | Which registry, and does it support **immutable tags, digest pinning and scheduled re-scan**? | Platform Engineering Lead | W1 | §4, `PE-004` §6.3 |
| Q-07 | Is a GPU node genuinely required for `INT-043` LLM inference, or is CPU inference acceptable at the expected volume? | Chief Architect | W6 | §6.1 `ml` pool, `PE-006` |

---

## 17. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The pre-existing state is **measured** | Opening table — **0 Dockerfiles, charts or manifests** in the estate |
| AC-02 | The image standard is specified, including the **`local` exception** | §3, §3.5 |
| AC-03 | Base image policy includes the **rebuild-dependents rule** and a way to verify it | `BI-03`, `FF-139` |
| AC-04 | The orchestration choice is argued from **`BD-R`**, not from preference | §5.2, `PE-005-D-02` |
| AC-05 | **Two clusters, not one stretched cluster**, with the residency reasoning stated | `CL-05`, `PE-005-D-06` |
| AC-06 | What does **not** run in the cluster is stated, with the consequence accepted | §5.5 |
| AC-07 | Resource model produces **`Guaranteed`** production pods, and autoscaling exclusions are argued | §7.1, §7.2, §7.3 |
| AC-08 | **`PE-004-F-02` is closed** — the readiness contract exists and is enforceable | §10, `FF-142` |
| AC-09 | The two counter-intuitive probe rules are stated with their failure modes | `RD-03`, `RD-04` |
| AC-10 | **The version treadmill is quantified** and assigned | §12, `PE-005-F-03` |
| AC-11 | Odoo's non-conformance to Twelve-Factor is stated rather than designed around silently | §13 |
| AC-12 | Fitness-function allocation was enumerated before allocation | §14 |

**Definition of done.** Complete when every criterion is met, **Q-01 and Q-02 are decided**,
`FF-137`…`FF-146` are enabled, Kubernetes and K3s are on `AR-013` §7's currency table (`VL-05`), and
`PGD-000`'s `PE-005` row carries a fresh enumeration timestamp.

---

## 18. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`PE-001`** §4, §9 | Zones, node placement, HA, `HB-02` |
| Upstream | **`PE-002`** | Cluster per environment |
| Upstream | **`PE-003`** §5.2, §10.1 | The `cluster/` module; the image boundary |
| Upstream | **`PE-004`** §6, §8 | Artefact rules; deployment strategy; **`PE-004-F-02` closed here** |
| Upstream | `BE-007` | Pinning, SBOM, vulnerability response, base-image currency |
| Upstream | `AR-013` | Licence rules; **`VL-05` adds Kubernetes to its currency table** |
| Downstream | **`PE-006`** | §7's resource model is the unit it sizes; `PE-005-F-02`'s pooler |
| Downstream | **`PE-007`** | `RC-05`'s registry replica; cluster rebuild in recovery |
| Downstream | **`PE-008`** | Probe observability; `CS-03`'s named agent exception; cluster audit logs |
| Downstream | **`PE-009`** | `CS-07`'s runtime secret mounting |
| Downstream | `SC-002`, `SC-005` | Container attack surface; admission control |
| Lateral | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §21.1, §21.3 | Component classes and HA — **§17.4's currency table lacks the orchestration platform** |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §7, §8.1 | Docker/K3s named; compute sizing |

---

## 19. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./PE-001_Infrastructure_and_Network_Architecture_Design.md`](./PE-001_Infrastructure_and_Network_Architecture_Design.md) ·
[`./PE-003_Infrastructure_as_Code_Standard.md`](./PE-003_Infrastructure_as_Code_Standard.md) ·
[`./PE-004_CI_CD_Pipeline_Design_Specification.md`](./PE-004_CI_CD_Pipeline_Design_Specification.md) ·
[`./PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md`](./PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md) ·
[`./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md`](./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) ·
[`./PE-008_Observability_and_Monitoring_Design.md`](./PE-008_Observability_and_Monitoring_Design.md) ·
[`../02_Architecture_and_Design/AR-013_Technology_Radar_and_Build_vs_Buy_Register.md`](../02_Architecture_and_Design/AR-013_Technology_Radar_and_Build_vs_Buy_Register.md)

**Workspace**
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §17.4, §21.1, §21.3 ·
`../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §7, §8.1

**External sources**

| Source | What it establishes | Verified |
|---|---|---|
| **Kubernetes support policy** | The **three most recent minor versions** are supported; each receives patches for about **14 months**; minors arrive roughly every 4 months | 2026-08-19 |
| **Kubernetes 1.34 end of life** | **27 October 2026** — currently supported alongside 1.35 and 1.36 | 2026-08-19 |
| **K3s** | Conformant lightweight Kubernetes tracking upstream; maintains the corresponding release lines; **Apache-2.0** | 2026-08-19 |
| OCI Image and Runtime Specifications | Image format and runtime contract | 2026-08-19 |
| NIST SP 800-190 | Application container security | 2026-08-19 |
| CIS Kubernetes Benchmark | Cluster hardening | 2026-08-19 |
| Twelve-Factor App §6, §8, §9, §11 | Stateless processes, concurrency, disposability, logs | 2026-08-19 |

---

## 20. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Platform Engineering | Initial issue against **0 Dockerfiles, charts or manifests** in the estate. Rules **K3s from Wave 1, argued from `BD-R`** — the only conformant option that runs identically in regional cloud and Bangladeshi colocation — and **two clusters rather than one stretched cluster**, making a regional `Z4` scheduling decision structurally impossible. **Closes `PE-004-F-02`** with a readiness contract whose two central rules are the opposite of the intuitive design. Rules stateful stores out of the cluster and Odoo as stateful-adjacent. **Quantifies the Kubernetes version treadmill at ~9 upgrades over 36 months, one inside Wave 1**, and records that the orchestration platform is absent from `AR-013`'s currency table (`PE-005-F-03`). Raises `PE-005-F-01` (`BD-R` registry reachability as a `PE-007` dependency) and `PE-005-F-02` (no connection pooler in any sizing table) | *Pending — CTO; `GV-002` not constituted* |

---

*`PE-005` · Category 10 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
