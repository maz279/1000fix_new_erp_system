# =============================================================================
# 1000fix-erp - Makefile (canonical targets, P02-M05-T10 / M06 / M10)
# Windows developers use tooling/scripts/tasks.ps1 -Target <name> (D-WS-001);
# both drive the SAME operations. If you change one, change the other.
# =============================================================================
SHELL := /bin/bash
.DEFAULT_GOAL := help
COMPOSE := docker compose -f infra/compose/docker-compose.yml
PROFILE ?= core
ODOO_BIN := vendor/odoo/odoo-bin
ODOO_CONF := infra/odoo-conf/local.conf
PY := python3

.PHONY: help bootstrap up down reset odoo-conf db-create odoo-init odoo-install-wave1 run seed test-smoke doctor upgrade vendor import-vendor verify-repo

help: ## this help
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-22s %s\n", $$1, $$2}'

bootstrap: ## P02-M06-T01: toolchains + uv sync + pnpm install + hooks + odoo-conf (budget 15-25 min)
	$(PY) tooling/scripts/setup-toolchains.sh 2>/dev/null || true
	uv sync
	pnpm install
	pre-commit install
	git config core.hooksPath .githooks
	$(MAKE) odoo-conf

up: ## P02-M05-T10: start PROFILE stacked on core (default core); DE-03 waits for health
	$(COMPOSE) --profile core $(if $(filter $(PROFILE),core),,--profile $(PROFILE)) up -d --wait

down: ## stop PROFILE
	$(COMPOSE) --profile $(PROFILE) down

reset: ## DE-05: COMPLETE INTENTIONAL RESET (down -v, recreate, reseed)
	$(COMPOSE) --profile $(PROFILE) down -v
	$(MAKE) up PROFILE=$(PROFILE)
	$(MAKE) db-create odoo-init odoo-install-wave1 seed

odoo-conf: ## REPO-15: regenerate infra/odoo-conf/local.conf (never hand-edit)
	$(PY) tooling/scripts/generate-odoo-conf.py

db-create: ## create fix_dev (UTF-8 enforced by the postgres image initdb args)
	$(COMPOSE) exec -T postgres psql -U fix -d postgres -c "SELECT 1 FROM pg_database WHERE datname='fix_dev'" | grep -q 1 || \
		$(COMPOSE) exec -T postgres createdb -U fix fix_dev

odoo-init: ## initialise Odoo on fix_dev (budget 15-30 min with wave 1 install)
	$(PY) $(ODOO_BIN) -c $(ODOO_CONF) -d fix_dev -i base --stop-after-init

odoo-install-wave1: ## install the Wave 1 module set (kernel + MV-moved)
	$(PY) $(ODOO_BIN) -c $(ODOO_CONF) -d fix_dev -i base,cd_party_master --stop-after-init || \
		echo "wave-1 install: extend the module list from cd-register.yaml wave=W1 items as they land"

run: ## serve http://127.0.0.1:8069 (dev=all: Python+XML reload without restart)
	$(PY) $(ODOO_BIN) -c $(ODOO_CONF) -d fix_dev

seed: ## P02-M06-T08: deterministic synthetic data (fixed seed, Bengali-first)
	$(PY) db/seeds/seed.py --seed 1000fix

test-smoke: ## P02-M10-T06: one path end-to-end, under 3 minutes
	$(PY) tooling/scripts/test-smoke.py

doctor: ## P02-M10-T01: all 14 checks; exit non-zero on any failure (DE-18/19)
	$(PY) tooling/scripts/doctor.py || bash tooling/scripts/doctor.sh

upgrade: ## upgrade one module after manifest/model/field edits (restart required)
	$(PY) $(ODOO_BIN) -c $(ODOO_CONF) -d fix_dev -u $(MODULE) --stop-after-init

vendor: ## P02-M04: import Odoo submodule + OCA subtrees (20-40 min first run)
	bash tooling/scripts/import-vendor.sh

verify-repo: ## run every repo fitness check (FF-*) in one pass
	$(PY) tooling/fitness/run.py
