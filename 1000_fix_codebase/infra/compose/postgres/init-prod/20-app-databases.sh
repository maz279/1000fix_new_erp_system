#!/usr/bin/env bash
# infra/compose/postgres/init-prod/20-app-databases.sh
#
# Production first-boot (initdb) only - mounted into /docker-entrypoint-initdb.d
# by infra/compose/docker-compose.prod.full.yml. Creates one least-privilege
# LOGIN role + database per application instead of letting every component use
# the superuser:
#   odoo       (CREATEDB, owns ${ODOO_DB})        - Odoo 19
#   keycloak   (owns keycloak)                    - Keycloak 26
#   telemetry  (owns fix_telemetry)               - telemetry-collector
# Passwords come from the container environment (compose `${VAR:?}`); none is
# stored here. CONNECT is revoked from PUBLIC so each role reaches only its own
# database. Re-running is not supported (initdb runs once per data volume).
# The postgres entrypoint SOURCES non-executable *.sh files, so no `set -u`
# here (it would leak into the entrypoint shell); the `:?` checks fail closed.
set -Eeo pipefail

: "${ODOO_DB:?ODOO_DB is required}"
: "${ODOO_DB_PASSWORD:?ODOO_DB_PASSWORD is required}"
: "${KEYCLOAK_DB_PASSWORD:?KEYCLOAK_DB_PASSWORD is required}"
: "${TELEMETRY_DB_PASSWORD:?TELEMETRY_DB_PASSWORD is required}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres \
  --set odoo_db="$ODOO_DB" \
  --set odoo_pw="$ODOO_DB_PASSWORD" \
  --set kc_pw="$KEYCLOAK_DB_PASSWORD" \
  --set tel_pw="$TELEMETRY_DB_PASSWORD" <<'SQL'
CREATE ROLE odoo LOGIN CREATEDB PASSWORD :'odoo_pw';
CREATE ROLE keycloak LOGIN PASSWORD :'kc_pw';
CREATE ROLE telemetry LOGIN PASSWORD :'tel_pw';

CREATE DATABASE :"odoo_db" OWNER odoo ENCODING 'UTF8' TEMPLATE template0
  LOCALE_PROVIDER icu ICU_LOCALE 'en-US';
CREATE DATABASE keycloak OWNER keycloak ENCODING 'UTF8' TEMPLATE template0;
CREATE DATABASE fix_telemetry OWNER telemetry ENCODING 'UTF8' TEMPLATE template0;

REVOKE CONNECT ON DATABASE :"odoo_db" FROM PUBLIC;
REVOKE CONNECT ON DATABASE keycloak FROM PUBLIC;
REVOKE CONNECT ON DATABASE fix_telemetry FROM PUBLIC;
GRANT CONNECT ON DATABASE :"odoo_db" TO odoo;
GRANT CONNECT ON DATABASE keycloak TO keycloak;
GRANT CONNECT ON DATABASE fix_telemetry TO telemetry;
SQL
echo "20-app-databases: roles odoo/keycloak/telemetry and their databases created"
