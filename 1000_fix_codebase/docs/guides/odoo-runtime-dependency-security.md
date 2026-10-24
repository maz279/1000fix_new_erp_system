# Odoo Runtime Dependency Security

| | |
|---|---|
| **Purpose** | The Python packages Odoo runs on are free of known vulnerabilities, without editing `vendor/` |
| **Origin** | R01 phase re-audit, 2026-10-22 |
| **Files** | `tooling/ci/odoo-security-overrides.txt` (the overrides), `infra/docker/odoo/` (the image), `tooling/tests/test_odoo_security_overrides.py` (lock-consistency test) |
| **Enforced by** | `.github/workflows/ci.yml` (every Odoo install + the `security` job), `tooling/ci/validate-workflow.py` check W9 |

## 1. Findings (2026-10-22)

| | Finding | Status |
|---|---|---|
| A | `vendor/odoo/requirements.txt` pins Python 3.12 to the Ubuntu 24.04 package set. pip-audit over the resolved Linux set found **130 entries (80 distinct advisories) in 14 packages**: werkzeug, pillow, urllib3, requests, jinja2, cryptography, pyopenssl, lxml, lxml-html-clean, idna, cbor2, PyPDF2, python-ldap, zeep. CI installed exactly these, and its `pip-audit` read only the uv lock, so nothing ever audited Odoo's runtime set. | Fixed: overrides + audit of the effective set |
| B | The uv lock (dev group, `signxml` for corporate-sso SAML) holds cryptography 50.0.2 / lxml 6.1.3. Installing Odoo's pins after `uv sync` downgraded cryptography, lxml, idna, requests and urllib3 and added pyOpenSSL 24.1.0, which needs cryptography<43. Every later `uv run` re-synced the locked versions, so CI ran a mixed set: `uv pip check` reported "signxml requires cryptography>=45, 42.0.8 installed". | Fixed: shared packages are pinned to the lock, and CI checks it |
| C | No Dockerfile built `1000fix/odoo`, which nine compose overlays reference. | Fixed: `infra/docker/odoo/Dockerfile` |

## 2. Override policy

`vendor/` is read-only (FF-03), so the fix is applied at install time with
uv's `--override`. An override replaces **every** requirement on that package,
whether direct or transitive, including its markers:

```bash
uv pip install -r vendor/odoo/requirements.txt \
    --override tooling/ci/odoo-security-overrides.txt
```

Never install Odoo's requirements without the override, on a runner, in the
image, or in a local venv.

Each pin follows the first of these rules that applies:

1. **In uv.lock too: pin exactly the locked version.** `uv run` re-syncs locked
   packages, so any other value leaves two competing versions (finding B).
   This covers cryptography, lxml, idna, requests and urllib3.
2. **Else: Odoo 19's own newer-Python pin**, if that pin is already patched.
   None of them were: Pillow 11.1.0/12.1.1, zeep 4.3.1 and pypdf 5.4.0 all
   still carry advisories.
3. **Else: the lowest version that clears every known advisory.**

Two further rules:

- **Exact pins only.** Each override is `==`, or a removal written as
  `name ; sys_platform == 'never'`.
- **Keep Odoo's platform markers.** For example, python-ldap stays
  `sys_platform != 'win32'`.

| Package | Odoo pin | Override | Why |
|---|---|---|---|
| cryptography | 42.0.8 | 50.0.2 | 7 advisories (fixed by 49.0.0); rule 1 (lock) |
| lxml | 5.2.1 | 6.1.3 | CVE-2026-41066 (6.1.0); rule 1 |
| idna | 3.6 | 3.20 | CVE-2024-3651, CVE-2026-45409 (3.15); rule 1 |
| requests | 2.31.0 | 2.34.2 | 3 advisories (2.33.0); rule 1 |
| urllib3 | 2.0.7 | 2.8.0 | 8 advisories (2.8.0); rule 1 |
| pyopenssl | 24.1.0 | 26.4.0 | CVE-2026-27448/27459 (26.0.0). 26.4.0 is the only release accepting cryptography 50.x |
| werkzeug | 3.0.1 | 3.1.9 | 7 advisories, the newest CVE-2026-102598 (3.1.9) |
| pillow | 10.2.0 | 13.0.0 | 37 advisories; 22 are fixed only in 13.0.0 |
| jinja2 | 3.1.2 | 3.1.6 | 5 advisories (3.1.6) |
| cbor2 | 5.6.2 | 5.9.0 | 3 advisories (5.9.0) |
| zeep | 4.2.1 | 4.3.3 | CVE-2026-58501 (4.3.3) |
| python-ldap | 3.4.4 | 3.4.5 | CVE-2025-61911/61912; Linux only |
| lxml-html-clean | unpinned (resolved 0.4.4) | 0.4.5 | CVE-2026-49825 |
| PyPDF2 → pypdf | 2.12.1 | removed; pypdf 6.21.1 | PyPDF2 is abandoned and CVE-2023-36464 is fixed only in pypdf. Odoo 19 supports pypdf (`odoo/tools/pdf/_pypdf.py`, its own py3.13+ choice). 6.21.1 is the lowest release clearing all 56 pypdf advisories |

The comments in the overrides file list the advisory IDs for each pin.

**Compatibility notes.** `odoo/_monkeypatches/OpenSSL.py` skips its shim for
pyOpenSSL ≥ 24.3. `urllib3.contrib.pyopenssl`, which ir_mail_server uses for
certificate auth, still ships in urllib3 2.8. Odoo 19 already pins lxml 6.0.2
for Python 3.14.

OCA `report_py3o` imports PyPDF2 only to merge multi-report output, and falls
back to a debug log without it. No `cd_*` addon installs it.

## 3. How CI enforces it

- **Every install is overridden.** Each job that installs Odoo's requirements
  (model-registry, unit, integration, nightly-journeys, security) runs the
  command above. The jobs first `apt-get install libldap2-dev libsasl2-dev
  libpq-dev`, because python-ldap and psycopg2 publish no wheels.
- **The security job audits what actually runs.** It runs:
  1. `uv sync --frozen`
  2. the overridden Odoo install
  3. `uv sync --frozen --inexact --check`, which fails if the Odoo install
     moved any locked package
  4. `uv run --no-sync pip-audit`, which audits the whole environment (lock
     plus effective Odoo set), exactly as installed
- **The workflow can't regress silently.** `validate-workflow.py` W9 fails on
  an Odoo install without `--override tooling/ci/odoo-security-overrides.txt`,
  or a `pip-audit` step that runs before that install.
- **Overrides and lock can't drift.** `tooling/tests/test_odoo_security_overrides.py`
  (in the unit job's `pytest tooling`) fails when an override and uv.lock
  disagree, and when an image extra is not the locked version.

## 4. Refreshing (whenever pip-audit or a lock bump flags something)

1. **Audit the effective set on both platforms.** Resolve it, then audit each
   file:
   ```bash
   uv pip compile vendor/odoo/requirements.txt --override tooling/ci/odoo-security-overrides.txt \
       --python-version 3.12 --python-platform x86_64-manylinux_2_28 -o linux.txt
   uv pip compile vendor/odoo/requirements.txt --override tooling/ci/odoo-security-overrides.txt \
       --python-version 3.12 --python-platform windows -o windows.txt
   uvx --system-certs --with pip-system-certs pip-audit -r linux.txt --no-deps --disable-pip --progress-spinner off
   ```
   Run the same `pip-audit` command for `windows.txt`.
2. **Pick each fix by the rules in §2.** For a package that is also in the
   lock, bump the lock first (`uv lock --upgrade-package <name>`), then copy
   the locked version into the override.
3. **Check transitive limits.** pyOpenSSL, for example, caps cryptography. The
   `uv pip check` result must be clean.
4. **Validate in an isolated venv**, never in the shared interpreter:
   1. Install the lock export, then the overridden Odoo set.
   2. Run `tooling/scripts/build-test-db.py --db fix_test_<x>`. All 71 `cd_*`
      addons must install.
   3. Run the full suite with `FIX_TEST_DB=fix_test_<x>`, and compare its
      failures with a run on the old pins.
   4. Smoke a live server: login, JSON-RPC/XML-RPC, a PDF merge, an image
      resize and an outgoing mail server connection.
   5. Rebuild the image.

Local venvs install the same way: `uv sync`, then the override command above.

On Windows, `zoneinfo` has no system database: uv.lock carries `tzdata` for
`sys_platform == 'win32'` (added 2026-10-22), so `uv sync` covers it.

## 5. The image: `infra/docker/odoo/Dockerfile`

**Build.** Run from the codebase root:

```bash
docker build -f infra/docker/odoo/Dockerfile -t 1000fix/odoo:19.0-dev .
```

Or use `docker compose build` with any overlay. The nine `odoo-*` services
carry `build:` and keep their image tags.

**Context.** `Dockerfile.dockerignore` is an allowlist. Only `vendor/odoo`,
`vendor/oca`, `addons`, `libs`, `services` and the few files the image reads
are sent to the daemon.

**Behind a TLS-inspecting proxy** (for example, antivirus HTTPS scanning), add
`--secret id=extra_ca,src=<root-ca.pem>`. The CA is used only for the
download steps and never lands in a layer.

**Base image.** `python:3.12-slim-bookworm` (Debian 12) at the
`DOCKERFILE_DIGEST_python_3.12-slim-bookworm` pin. Bookworm, not trixie,
because it is the newest Debian with a wkhtmltopdf 0.12.6.1-3 build. It is
*oldstable*: Debian LTS security support runs to 2028-06-30. The uv build
stage is pinned by digest in `versions.lock` too.

**Python.** The image installs Odoo's requirements plus the overrides, plus
`requirements-first-party.txt`. That file adds PyYAML, which
`cd_workflow_engine` imports. `uv pip check` must pass at build time.

**System packages.**

- Database and LDAP: libpq5, libldap-2.5-0 and libsasl2-2.
- File type detection: libmagic.
- Health check: curl.
- **PDF engine: wkhtmltopdf 0.12.6.1-3 (patched Qt)**, the bookworm amd64
  `.deb`. `infra/docker/odoo/fetch-pinned.py` downloads it with the URL and
  SHA256 from `versions.lock` (`WORKSTATION_WKHTMLTOPDF_CONTAINER_BOOKWORM_*`)
  and verifies it before install. The build fails unless
  `wkhtmltopdf --version` reports patched Qt. Its runtime dependencies come
  from Debian.
- Fonts: fontconfig, DejaVu, and two Bengali families: Debian's
  **`fonts-noto-core` Noto Sans Bengali** and Lohit Bengali (the BE-001 Linux
  baseline). Inside the image, system fonts serve only the PDF engine, because
  the web client ships its own web fonts. They must therefore be fonts
  wkhtmltopdf's Qt 4.8 can shape; see §6.

**User and code.** The container runs as the non-root user `odoo` (uid 10001).
The code is root-owned and precompiled. Odoo writes only to `/var/lib/odoo`.

**Entrypoint** (`entrypoint.py`):

- **DE-11 environment guard.** It refuses to start (exit 42) unless `FIX_ENV`
  names an environment in `infra/environments.yaml`. With `FIX_ENV=local` it
  also runs `libs/py/fix_env_guard` over the endpoint variables and the
  database `HOST`.
- **Generated conf (REPO-15).** It writes the conf at start:
  - `addons_path` comes from `generate-odoo-conf.py`.
  - The database settings come from `HOST`/`PORT`/`USER`/`PASSWORD`.
  - `list_db` is on only for `local`.
  - `admin_passwd` is random unless `ODOO_ADMIN_PASSWORD` is set.
- **Arguments.** Arguments that start with `-` go to `odoo-bin`, for example
  compose's `--load=base,rpc,web,cd_entity_config`.

**Digest.** The `1000fix/odoo` digest stays `PENDING-FIRST-BUILD` until the
first registry push (`digest-pinning-policy.md`).

## 6. Known gaps

- **The wkhtmltopdf pin is trust-on-first-download.** Upstream publishes no
  checksum for the bookworm `.deb`. The pin is the SHA256 of the release
  asset, fetched twice on 2026-10-22 with identical results. The jammy `.deb`
  in `versions.lock` is corroborated by Odoo's official Dockerfile, but it
  cannot install on Debian, because `libjpeg-turbo8` does not exist there.
  wkhtmltopdf is also archived upstream and has known CVEs. Odoo 19 still
  needs it for QWeb PDFs, so a replacement PDF engine is a separate decision.
- **The workstation's Noto Sans Bengali v3.011 cannot be used by
  wkhtmltopdf.** Measured 2026-10-22 with wkhtmltopdf 0.12.6 and all builds
  from the pinned `versions.lock` zip:
  - The hinted TTF, unhinted TTF and OTF builds render as `.notdef` boxes, and
    their ToUnicode maps hold only the space glyph.
  - The `full` TTF build renders, but its conjuncts are unshaped (visible
    hasant).

  Debian's 2020 Noto Sans Bengali (`fonts-noto-core`) and Lohit Bengali both
  shape conjuncts, reph and pre-base vowels correctly. So the image uses those,
  and the v3.011 pin stays a workstation and browser font. PDFs therefore use
  an older Noto build than the screens. If TR-07 requires one version
  everywhere, that needs a ruling, for example a different PDF engine.
- **PDF text extraction is lossy for Bengali.** Text is extractable (pypdf
  finds the labels and data), but conjuncts and pre-base vowels come out in
  visual order: রহিম reads as "রিহম". This is normal for shaped Indic text in
  PDF. It matters only for machine reading, not for the printed page.
- **The Bengali QWeb reports had layout defects, fixed 2026-10-22.** Each was
  verified by rasterising page 1 rendered in the container.
  - **The job card (`cd_service_order.report_jobcard`) had three:**
    1. `t-field` was set directly on `<td>`, which Odoo 19 QWeb refuses, so
       the report raised a 500.
    2. There was no `div.article` (see the next item).
    3. Its title block was an Odoo running `div.header`, rendered into the
       6 mm top margin, so it was clipped. It is now inline at the top of the
       card.
  - **Mushak 6.3, Mushak 6.6 and the s.52 certificate (`cd_tax_engine_bd`)
    also had no `div.article`.**

  Without `div.article`, Odoo hands the body to wkhtmltopdf without
  `web.minimal_layout`. That means no `<meta charset>`, so every Bengali label
  printed as Latin-1 mojibake. It also means no report assets, so
  `statutory_bn.css`, its table borders and the monospace identifiers were
  never applied. All four reports now render on one page with no clipping or
  overflow, correctly shaped Bengali, and the statutory CSS applied.
