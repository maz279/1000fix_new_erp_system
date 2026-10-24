# =============================================================================
# 1000fix/odoo - Odoo 19 + OCA + first-party addons (R01 re-audit 2026-10-22)
#
# Build from the CODEBASE ROOT (the context must hold vendor/, addons/ ...):
#   docker build -f infra/docker/odoo/Dockerfile -t 1000fix/odoo:19.0-dev .
# The nine infra/compose odoo-* services carry the same `build:`.
# Context: Dockerfile.dockerignore next to this file (BuildKit) is an
# ALLOWLIST - node_modules, .venv, infra/odoo-data, apps/, coverage ... never
# leave the workstation.
#
# Python: vendor/odoo/requirements.txt WITH tooling/ci/odoo-security-overrides.txt
# (the exact set CI tests and pip-audits; docs/guides/odoo-runtime-dependency-
# security.md) + requirements-first-party.txt. vendor/ is copied, never edited.
#
# Base: python:3.12-slim-bookworm (Debian 12) at the versions.lock
# DOCKERFILE_DIGEST_python_3.12-slim-bookworm digest. Bookworm, not trixie,
# because it is the newest Debian with a wkhtmltopdf 0.12.6.1-3 (patched Qt)
# build; it is oldstable - Debian LTS security support to 2028-06-30. Every
# FROM is digest-pinned (DE-06).
#
# wkhtmltopdf: the 0.12.6.1-3 bookworm amd64 .deb, URL + SHA256 from
# versions.lock (WORKSTATION_WKHTMLTOPDF_CONTAINER_BOOKWORM_*), verified before
# use; the build fails unless `wkhtmltopdf --version` reports patched Qt.
#
# Runtime contract (= the official Odoo image, which infra/compose assumes):
#   FIX_ENV (required, DE-11) - HOST / PORT / USER / PASSWORD (database)
#   ODOO_ADMIN_PASSWORD (optional; unset = random), ODOO_WORKERS (optional)
#   args starting with '-' go to odoo-bin;  volume /var/lib/odoo (data_dir)
# =============================================================================

FROM ghcr.io/astral-sh/uv:0.12.13@sha256:b485bd65cc2cf1c9a93b3554012c9c3778cf7b1b5fd3d3096ce9e1226c97e1e6 AS uv

# ---- build: venv, sdist-only packages (psycopg2, python-ldap), pinned downloads
FROM python:3.12-slim-bookworm@sha256:6a0e06f5ba0b373d051aabd3fffb9b873f27f9a2a3a14bcbe37dee6f0e3bbc70 AS build
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libc6-dev libpq-dev libldap2-dev libsasl2-dev \
 && rm -rf /var/lib/apt/lists/*
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never UV_NO_CACHE=1
WORKDIR /src
# A workstation behind a TLS-inspecting proxy/antivirus passes that proxy's
# PUBLIC root CA as an optional build secret - used for the HTTPS steps below
# only, never written to a layer; CI runners pass nothing:
#   docker build --secret id=extra_ca,src=<root-ca.pem> -f infra/docker/odoo/Dockerfile .
# (the hash pins still verify every byte fetched through it)
COPY vendor/odoo/requirements.txt vendor/odoo/requirements.txt
COPY tooling/ci/odoo-security-overrides.txt tooling/ci/odoo-security-overrides.txt
COPY infra/docker/odoo/requirements-first-party.txt infra/docker/odoo/requirements-first-party.txt
RUN --mount=type=secret,id=extra_ca,required=false \
    if [ -s /run/secrets/extra_ca ]; then \
      cat /etc/ssl/certs/ca-certificates.crt /run/secrets/extra_ca > /tmp/ca.pem \
      && export SSL_CERT_FILE=/tmp/ca.pem; \
    fi \
 && uv venv /opt/venv --python /usr/local/bin/python3.12 \
 && uv pip install --python /opt/venv/bin/python \
      -r vendor/odoo/requirements.txt \
      -r infra/docker/odoo/requirements-first-party.txt \
      --override tooling/ci/odoo-security-overrides.txt \
 && uv pip check --python /opt/venv/bin/python \
 && rm -f /tmp/ca.pem
# Pinned artefact of versions.lock: the wkhtmltopdf .deb.
COPY tooling/versions.lock tooling/versions.lock
COPY infra/docker/odoo/fetch-pinned.py /tmp/fetch-pinned.py
RUN --mount=type=secret,id=extra_ca,required=false \
    [ "$(dpkg --print-architecture)" = amd64 ] \
      || { echo "only the amd64 wkhtmltopdf build is pinned in versions.lock"; exit 1; } \
 && if [ -s /run/secrets/extra_ca ]; then \
      cat /etc/ssl/certs/ca-certificates.crt /run/secrets/extra_ca > /tmp/ca.pem \
      && export SSL_CERT_FILE=/tmp/ca.pem; \
    fi \
 && python /tmp/fetch-pinned.py tooling/versions.lock \
      WORKSTATION_WKHTMLTOPDF_CONTAINER_BOOKWORM_URL_AMD64 \
      WORKSTATION_WKHTMLTOPDF_CONTAINER_BOOKWORM_SHA256_AMD64 \
      /pkgs/wkhtmltox.deb \
 && rm -f /tmp/ca.pem

# ---- runtime ------------------------------------------------------------------
FROM python:3.12-slim-bookworm@sha256:6a0e06f5ba0b373d051aabd3fffb9b873f27f9a2a3a14bcbe37dee6f0e3bbc70 AS runtime
# libpq5 (psycopg2) - libldap-2.5-0 + libsasl2-2 (python-ldap) - libmagic1
# (python-magic: upload MIME sniffing) - curl (health checks) - fontconfig +
# fonts-dejavu-core (Latin). wkhtmltopdf's own Depends (X11 render libs,
# libjpeg62-turbo, libssl3, xfonts-75dpi/base) come from Debian via apt; the
# .deb is bind-mounted from the build stage, so it never lands in a layer.
# Pillow / lxml / cryptography wheels bundle their own libjpeg, zlib, libxml2
# and OpenSSL: no -dev packages here.
#
# Bengali (TR-07) - server-side fonts serve ONLY the PDF engine (the web client
# ships its own web fonts), so they must be fonts wkhtmltopdf's Qt 4.8 shapes:
#   fonts-noto-core  Debian's signed Noto Sans Bengali (BE-001 Linux baseline) -
#                    conjuncts, reph and pre-base vowels shape correctly
#   fonts-lohit-beng-bengali  second family (BE-001), shapes correctly too
# NOT the workstation pin NotoSansBengali-v3.011 (versions.lock): measured
# 2026-10-22, its hinted/unhinted TTF and OTF builds render as .notdef boxes
# in wkhtmltopdf 0.12.6 and its "full" build renders unshaped conjuncts
# (visible hasant) - see docs/guides/odoo-runtime-dependency-security.md.
RUN --mount=type=bind,from=build,source=/pkgs,target=/pkgs \
    apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl libpq5 libldap-2.5-0 \
      libsasl2-2 libmagic1 fontconfig fonts-dejavu-core fonts-noto-core \
      fonts-lohit-beng-bengali /pkgs/wkhtmltox.deb \
 && rm -rf /var/lib/apt/lists/* \
 && wkhtmltopdf --version | grep -q "with patched qt" \
 && wkhtmltopdf --version \
 && fc-match -f '%{file}\n' 'Noto Sans Bengali' | grep -q '/noto/NotoSansBengali'
RUN fc-cache -f \
 && groupadd --system --gid 10001 odoo \
 && useradd --system --uid 10001 --gid odoo --home-dir /var/lib/odoo --shell /usr/sbin/nologin odoo \
 && install -d -o odoo -g odoo -m 0750 /var/lib/odoo \
 && install -d -o odoo -g odoo -m 0700 /etc/odoo
COPY --from=build /opt/venv /opt/venv
# Code is root-owned and read-only to the odoo user; Odoo writes only data_dir.
WORKDIR /opt/1000fix
COPY vendor/odoo vendor/odoo
COPY vendor/oca vendor/oca
COPY libs libs
COPY services services
COPY addons addons
COPY infra/environments.yaml infra/environments.yaml
COPY tooling/scripts/generate-odoo-conf.py tooling/scripts/generate-odoo-conf.py
COPY infra/docker/odoo/entrypoint.py /usr/local/bin/fix-odoo-entrypoint
# Precompile: the non-root user cannot write __pycache__ next to the code.
RUN /opt/venv/bin/python -m compileall -q -j 0 vendor libs services addons tooling >/dev/null \
 && chmod 0755 /usr/local/bin/fix-odoo-entrypoint
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONPATH=/opt/1000fix \
    PYTHONUNBUFFERED=1 \
    ODOO_RC=/etc/odoo/odoo.conf
USER odoo
VOLUME ["/var/lib/odoo"]
EXPOSE 8069 8072
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8069/web/health || exit 1
ENTRYPOINT ["/opt/venv/bin/python", "/usr/local/bin/fix-odoo-entrypoint"]
CMD []
