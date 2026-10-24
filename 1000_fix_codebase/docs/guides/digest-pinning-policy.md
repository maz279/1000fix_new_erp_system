# Container Image Digest-Pinning Policy

| | |
|---|---|
| **Purpose** | Every image reference in `infra/compose/*.yml` is either digest-pinned from a real registry, or explicitly marked pending — never a fabricated digest |
| **Origin** | R01 audit correction, 2026-10-21 (audit finding: 11 compose files carried synthetic sequential-hex sha256 values that passed the `PLACEHOLDER-RESOLVE` grep but would fail any real `docker compose pull`) |
| **Tools** | `tooling/scripts/resolve-digests.ps1` (registry resolution), `tooling/versions.lock [compose-digests]` (pin record) |

## Rules

1. **Registry images are digest-pinned from the live registry.** Digests come
   from `docker buildx imagetools inspect` / the registry API, recorded in
   `tooling/versions.lock [compose-digests]`, never hand-typed.
2. **Locally-built images cannot be digest-pinned before they exist.** The nine
   `1000fix/odoo:19.0-*` environment images are built in-house. Until the first
   `docker push` to a registry, their compose entries carry the tag plus an
   inline comment:
   `# digest PENDING-FIRST-BUILD: ...pin via resolve-digests.ps1 at first registry push`
   A fabricated sha256 is worse than an honest pending marker: it fails pulls,
   poisons reproducibility claims, and defeats audit greps.
3. **At first registry push**, run `tooling/scripts/resolve-digests.ps1`; it
   replaces pending markers/tags with the real digest and records it in
   `versions.lock`. The `stage-08-security` pipeline stage counts an image as
   compliant only when it carries `@sha256:` or an explicit `pending` marker.
4. **`PLACEHOLDER-RESOLVE` grep (G0b-9) is necessary but not sufficient** —
   passing it only means no unresolved placeholder remains; it says nothing
   about digest authenticity.

## Digests resolved on 2026-10-21 (live registry queries)

| Image | Digest (sha256 prefix) |
|---|---|
| `kong:3.8.0` | `322e8020…` (Docker Hub) |
| `nginx:1.27-alpine` | `65645c7b…` (Docker Hub) |
| `quay.io/keycloak/keycloak:26.0.0` | `db0d0f2c…` (quay.io; matches Docker Hub mirror) |
| `hashicorp/vault:1.18.1` | `3580fa35…` (Docker Hub) |

## Pending

| Image | Status |
|---|---|
| `1000fix/odoo:19.0-dev/sit/uat/sandbox/staging/training/perf/prod/dr` | PENDING-FIRST-BUILD (9 images) — pin via `resolve-digests.ps1` after the first registry push |
