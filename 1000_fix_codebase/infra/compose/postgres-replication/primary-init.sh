#!/usr/bin/env bash
# =============================================================================
# 1000fix-erp - PostgreSQL streaming-replication PRIMARY setup (R01 DR audit)
#
# Mounted read-only into /docker-entrypoint-initdb.d/ of a primary
# (postgres-prod, postgres-ha-primary). The official image runs it ONCE, when
# it initialises an empty data directory (temp server up, local socket only).
# It is idempotent, so it can also be run by hand against an already
# initialised primary:
#   docker compose exec postgres-prod bash /docker-entrypoint-initdb.d/10-replication-primary.sh
#
# It makes the primary able to feed physical standbys:
#   1. a LOGIN REPLICATION role; name + password come from the environment
#      (the password is Vault injected - never a literal in compose). The role
#      also gets pg_monitor so the standby healthcheck can read
#      pg_stat_wal_receiver.status on the clone.
#   2. one physical replication slot per standby (reserved immediately), so
#      the primary keeps the WAL a disconnected standby still needs - bounded
#      by max_slot_wal_keep_size on the primary's command line.
#   3. a pg_hba.conf `replication` entry for that role ONLY, scram-sha-256,
#      scoped by default to `samenet`: the subnets the server is directly
#      attached to, i.e. the compose network. A standby on another site sets
#      PG_REPLICATION_ALLOWED_ADDRESS to its CIDR instead.
#
# wal_level / max_wal_senders / max_replication_slots are server settings and
# stay `-c` flags on the primary's compose command.
#
# Environment:
#   PG_REPLICATION_USER             replication role name            (required)
#   PG_REPLICATION_PASSWORD         replication role password        (required)
#   PG_REPLICATION_SLOTS            comma-separated slot names       (required)
#   PG_REPLICATION_ALLOWED_ADDRESS  pg_hba address field   (default: samenet)
#   PG_REPLICATION_HBA_TYPE         host | hostssl         (default: host)
#
# The body runs in a subshell: docker-entrypoint.sh SOURCES non-executable
# init files, and strict-mode options or variables must not leak into it.
# =============================================================================

replication_primary_setup() (
	set -Eeuo pipefail

	die() {
		echo "replication-primary: $*" >&2
		exit 1
	}

	: "${PG_REPLICATION_USER:?PG_REPLICATION_USER must be set}"
	: "${PG_REPLICATION_PASSWORD:?PG_REPLICATION_PASSWORD must be set (Vault injected)}"
	: "${PG_REPLICATION_SLOTS:?PG_REPLICATION_SLOTS must name at least one slot}"
	local hba_type="${PG_REPLICATION_HBA_TYPE:-host}"
	local hba_address="${PG_REPLICATION_ALLOWED_ADDRESS:-samenet}"

	# Validate everything that ends up in pg_hba.conf or in SQL identifiers.
	[[ $PG_REPLICATION_USER =~ ^[a-z_][a-z0-9_]{0,62}$ ]] ||
		die "PG_REPLICATION_USER '$PG_REPLICATION_USER' is not a plain lower-case identifier"
	[[ $hba_type == host || $hba_type == hostssl ]] ||
		die "PG_REPLICATION_HBA_TYPE must be host or hostssl, got '$hba_type'"
	[[ $hba_address =~ ^[A-Za-z0-9.:/_-]+$ ]] ||
		die "PG_REPLICATION_ALLOWED_ADDRESS '$hba_address' is not a single pg_hba address"
	[[ $PG_REPLICATION_PASSWORD != *$'\n'* ]] || die "PG_REPLICATION_PASSWORD must be a single line"

	local psql_admin=(psql -X -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "${POSTGRES_DB:-$POSTGRES_USER}")

	# 1. role. psql reads the password from the environment (\getenv), so it
	#    never appears on a command line; :'repl_password' quotes it as a
	#    literal. password_encryption is scram-sha-256 (PG17 default).
	"${psql_admin[@]}" -v repl_user="$PG_REPLICATION_USER" <<-'SQL'
		\getenv repl_password PG_REPLICATION_PASSWORD
		SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'repl_user') AS repl_role_exists \gset
		\if :repl_role_exists
		ALTER ROLE :"repl_user" WITH LOGIN REPLICATION PASSWORD :'repl_password';
		\else
		CREATE ROLE :"repl_user" WITH LOGIN REPLICATION PASSWORD :'repl_password';
		\endif
		GRANT pg_monitor TO :"repl_user";
	SQL

	# 2. one physical slot per standby, WAL reserved from creation.
	local slots slot
	IFS=',' read -r -a slots <<<"$PG_REPLICATION_SLOTS"
	for slot in "${slots[@]}"; do
		slot="${slot//[[:space:]]/}"
		[[ -z $slot ]] && continue
		[[ $slot =~ ^[a-z0-9_]{1,63}$ ]] || die "slot name '$slot' is invalid (a-z, 0-9, _)"
		"${psql_admin[@]}" -v slot="$slot" <<-'SQL'
			SELECT pg_create_physical_replication_slot(:'slot', true)
			WHERE NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = :'slot');
		SQL
	done

	# 3. pg_hba.conf: replication connections for this role only.
	local hba_line="$hba_type replication $PG_REPLICATION_USER $hba_address scram-sha-256"
	local hba_file
	hba_file="$("${psql_admin[@]}" -tAc 'SHOW hba_file')"
	if ! grep -qxF "$hba_line" "$hba_file"; then
		printf '\n# streaming replication (infra/compose/postgres-replication/primary-init.sh)\n%s\n' \
			"$hba_line" >>"$hba_file"
	fi
	"${psql_admin[@]}" -tAc 'SELECT pg_reload_conf()' >/dev/null

	echo "replication-primary: role '$PG_REPLICATION_USER', slot(s) '$PG_REPLICATION_SLOTS', pg_hba '$hba_line'"
)

replication_primary_setup
