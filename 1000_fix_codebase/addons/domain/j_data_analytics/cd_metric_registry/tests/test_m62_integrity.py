"""cd_metric_registry integrity tests — the seed-residue repair and the guards
that keep the impossible states out (A11 deep audit A3-F04/F06/F10, 2026-11-23).

The live estates carry rows no model path can produce: five metric definitions
"published" with no version, three contracts "active" with no producer
signature, four pipelines stamped with a last success no run produced, three
quality rules "passing" that were never measured — every one of them hanging
off one unrelated entity. The guards, the repair method, the quality runner
and the retention disposition are each driven here through the live ORM, with
the residue written the way the seeder wrote it (straight to SQL), because the
guards refuse it through the ORM.
"""

import datetime
import logging
import re

import pytest
from odoo import fields
from odoo.exceptions import UserError, ValidationError

OFFICER = "cd_metric_registry.group_data_governance_officer"
DOA_ADMIN = "cd_workflow_engine.group_doa_administrator"
MODULE_LOGGER = "odoo.addons.cd_metric_registry.models."
RULE_LOG = logging.getLogger(MODULE_LOGGER + "fix_metric_registry")
REPAIR_LOG = logging.getLogger(MODULE_LOGGER + "fix_data_platform")

# The residue, exactly as fix_real and fix_dev carry it (SQL, 2026-11-23).
SEED_ENTITIES = (
    # name, type, owner module, classification
    ("Service Orders Table", "table", "M01 Service Requests", "internal"),
    ("Customer API Resource", "api", "M33 Party Master", "confidential"),
    ("Order Events Stream", "event", "M01 Service Requests", "internal"),
    ("SLA Attainment KPI", "report", "M25 Business Intelligence", "internal"),
    ("Identity Documents", "document", "M33 Party Master", "residency_classified"),
)
SEED_HUB = "Customer API Resource"
SEED_PIPELINES = (
    # code, name, source system, load mode, schedule, SLO minutes
    ("PL-SO-CDC", "Service orders CDC", "odoo_fix.service_order", "cdc", "realtime", 15),
    ("PL-INV-DAILY", "Inventory snapshot", "odoo_fix.stock_quant", "full", "daily", 1440),
    (
        "PL-AR-INCR",
        "AR invoices incremental",
        "odoo_fix.account_move",
        "incremental",
        "hourly",
        120,
    ),
    ("PL-BKASH", "bKash settlement files", "bkash.sftp.settlement", "incremental", "daily", 1440),
)
SEED_RULES = (
    # name, type, seeded last result
    ("Orders Complete", "completeness", 10.0),
    ("Customer Unique", "uniqueness", 0.0),
    ("Events Fresh", "timeliness", 120.0),
)
SEED_CONTRACTS = (
    # dataset code, name, producer, schema version, SLO minutes
    ("DS-SERVICE-ORDER", "Service order events", "Service Platform (M01)", "2.1", 15),
    ("DS-AR-INVOICE", "AR invoice ledger", "Finance (M20)", "1.4", 120),
    ("DS-INVENTORY-SNAP", "Inventory snapshot", "Supply Chain (M15)", "1.0", 1440),
)
SEED_METRICS = (
    # code, name, domain, grain, definition, owner role
    (
        "MET-WIP-AGE",
        "WIP ageing (days)",
        "service",
        "day",
        "Mean of (now - order opened_at) over orders in an open state; numerator = sum "
        "of ages, denominator = open order count.",
        "R-05",
    ),
    (
        "MET-SLA-ATTAIN",
        "SLA attainment %",
        "service",
        "month",
        "Breached-free orders / all completed orders in the period; a breach is any "
        "stage exceeding its SLA clock.",
        "R-05",
    ),
    (
        "MET-AR-OVERDUE",
        "AR overdue %",
        "finance",
        "month",
        "Open receivable overdue / total open receivable at period end; overdue = due "
        "date passed by more than the grace days.",
        "R-26",
    ),
    (
        "MET-BENCH-UTIL",
        "Bench utilisation %",
        "service",
        "week",
        "Booked technician hours / available technician hours for the same workshop and week.",
        "R-09",
    ),
    (
        "MET-NPS",
        "Net promoter score",
        "customer",
        "quarter",
        "(Promoters - detractors) / responses; promoter = 9-10, detractor = 0-6.",
        "R-34",
    ),
)
SEED_POLICIES = (
    # entity name, name, tier, months, rate, volume, sentence
    (
        "Service Orders Table",
        "Retention - Service Orders",
        "hot",
        36,
        12.0,
        240,
        "archive after 36 months",
    ),
    (
        "Customer API Resource",
        "Retention - service_order",
        "hot",
        36,
        12.0,
        240,
        "archive after 36 months",
    ),
    (
        "Order Events Stream",
        "Retention - Order Events",
        "warm",
        84,
        8.0,
        120,
        "retain 7 years (tax), then archive",
    ),
    (
        "Identity Documents",
        "Retention - Identity Documents",
        "hot",
        84,
        12.0,
        60,
        "retain 7 years, then pseudonymise",
    ),
)
SEED_STAMP = datetime.datetime(2026, 10, 28, 15, 38, 30)
SEED_RULE_STAMP = datetime.datetime(2026, 10, 28, 15, 32, 30)


@pytest.fixture
def env(odoo_env):
    if "fix.data.entity" not in odoo_env:
        pytest.skip("cd_metric_registry is not installed")
    return odoo_env


@pytest.fixture
def make_user(env):
    counter = {"n": 0}

    def _make(*xmlids):
        counter["n"] += 1
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "M62 Integrity Probe %d" % counter["n"],
                    "login": "m62.integrity.%d@governance.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def officer(env, make_user):
    return make_user(OFFICER)


@pytest.fixture
def officer_b(env, make_user):
    """A second officer: the one who decides what the first requests."""
    return make_user(OFFICER)


def _sql(env, query, params=()):
    """Write a row the way the seeder did: past every model guard."""
    env.cr.execute(query, params)
    env.invalidate_all()


def _entity(env, name, **vals):
    return env["fix.data.entity"].create({"name": name, **vals})


def _decide(record, approver, comment="ok"):
    task = record.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == approver and t.state == "pending"
    )
    assert task, "no pending task for the deciding officer"
    task.with_user(approver).action_approve(comment=comment)


def live_residue(env):
    """The fix_real register, row for row. Nothing here could be created
    through the model guards any more, so the states go in by SQL."""
    created = {}
    for name, kind, owner, classification in SEED_ENTITIES:
        created[name] = _entity(
            env,
            name,
            entity_type=kind,
            owner_module=owner,
            classification=classification,
            retention_policy="7 years (statutory)",
        )
    # NOT the first entity alphabetically: the live seeder hung every register
    # off "Customer API Resource" (entities[0] of its own sorted search).
    hub = created[SEED_HUB]
    # every pipeline hangs off the hub, stamped with a success no run produced
    for code, name, source, mode, schedule, slo in SEED_PIPELINES:
        pipe = env["fix.data.pipeline"].create(
            {
                "code": code,
                "name": name,
                "source_system": source,
                "target_entity_id": hub.id,
                "load_mode": mode,
                "schedule": schedule,
                "freshness_sla_minutes": slo,
            }
        )
        _sql(
            env,
            "UPDATE fix_data_pipeline SET last_run_at = %s, last_success_at = %s WHERE id = %s",
            (SEED_STAMP, SEED_STAMP, pipe.id),
        )
    for name, kind, seeded in SEED_RULES:
        rule = env["fix.data.quality.rule"].create(
            {"name": name, "entity_id": hub.id, "rule_type": kind, "threshold": 95.0}
        )
        # 'passing' with a result nobody measured; last_measured is a true NULL
        _sql(
            env,
            "UPDATE fix_data_quality_rule SET state = 'passing', last_checked = %s, "
            "last_result = %s, last_measured = NULL WHERE id = %s",
            (SEED_RULE_STAMP, seeded, rule.id),
        )
    for code, name, producer, schema, slo in SEED_CONTRACTS:
        contract = env["fix.data.contract"].create(
            {
                "dataset_code": code,
                "name": name,
                "entity_id": hub.id,
                "producer": producer,
                "consumers": "BI (M25), Data Platform (M62)",
                "schema_version": schema,
                "guarantees": "Schema stable inside a major version; no NULL business keys",
                "freshness_sla_minutes": slo,
            }
        )
        _sql(env, "UPDATE fix_data_contract SET state = 'active' WHERE id = %s", (contract.id,))
    for code, name, area, grain, definition, role in SEED_METRICS:
        metric = env["fix.metric.definition"].create(
            {
                "code": code,
                "name": name,
                "domain_area": area,
                "grain": grain,
                "definition": definition,
                "source_entity_id": hub.id,
                "owner_role": role,
            }
        )
        _sql(
            env, "UPDATE fix_metric_definition SET state = 'published' WHERE id = %s", (metric.id,)
        )
    for entity_name, name, tier, months, rate, volume, sentence in SEED_POLICIES:
        entity = env["fix.data.entity"].search([("name", "=", entity_name)], limit=1)
        policy = env["fix.data.retention.policy"].create(
            {
                "name": name,
                "entity_id": entity.id,
                "tier": tier,
                "retention_months": months,
                "storage_cost_per_gb": rate,
                "volume_gb": volume,
                "purge_rule": sentence,
            }
        )
        # The live rows PREDATE the disposition field: they carry the prose and
        # the default 'retain', which is the state the repair derives from. The
        # cost column became Money later, so they carry no currency either.
        _sql(
            env,
            "UPDATE fix_data_retention_policy SET disposition = 'retain', "
            "currency_id = NULL WHERE id = %s",
            (policy.id,),
        )
    return hub


def residue_snapshot(env):
    """Every state the repair is allowed to touch, per model, for diffing."""
    out = {}
    for model in (
        "fix.data.entity",
        "fix.data.pipeline",
        "fix.data.quality.rule",
        "fix.data.contract",
        "fix.metric.definition",
        "fix.data.retention.policy",
    ):
        rows = env[model].search([], order="id")
        out[model] = {
            row.id: (
                row.write_date,
                {name: row[name] for name in models_fields(env, model)},
            )
            for row in rows
        }
    return out


def models_fields(env, model):
    return sorted(
        name
        for name, field in env[model]._fields.items()
        if field.store and field.type not in ("one2many", "many2many")
    )


def repair(env):
    return env["fix.data.entity"].action_repair_seed_residue()


class TestImpossibleStatesRefusedOnWrite:
    """A3-F04: the estates carry rows no model path can produce. The create
    guards already refuse a born-published metric, a born-active contract; the
    same states must not come back through a plain write either."""

    def test_a_published_definition_needs_a_published_version(self, env, officer):
        definition = (
            env["fix.metric.definition"]
            .with_user(officer)
            .create({"code": "MET-GUARD-1", "name": "x", "definition": "a / b"})
        )
        with pytest.raises(ValidationError, match="published"), env.cr.savepoint():
            definition.with_user(officer).write({"state": "published"})
        assert definition.state == "draft" and not definition.current_version_id

    def test_the_guard_holds_whatever_bypasses_the_write_path(self, env, officer):
        definition = (
            env["fix.metric.definition"]
            .with_user(officer)
            .create({"code": "MET-GUARD-2", "name": "x", "definition": "a / b"})
        )
        with pytest.raises(ValidationError, match="published"), env.cr.savepoint():
            definition.sudo().write({"state": "published"})
        assert definition.state == "draft"

    def test_an_active_contract_needs_the_producer_signature(self, env, officer):
        entity = _entity(env, "warehouse.fact_guard_contract")
        contract = (
            env["fix.data.contract"]
            .with_user(officer)
            .create(
                {
                    "dataset_code": "sales.guard",
                    "name": "guard",
                    "entity_id": entity.id,
                    "producer": "order service team",
                    "producer_signatory_id": officer.id,
                    "schema_version": "1.0",
                }
            )
        )
        # the engine's own flag: the only write path that reaches 'active'
        with pytest.raises(ValidationError, match="UNSIGNED"), env.cr.savepoint():
            contract.with_context(fix_contract_activation=True).write({"state": "active"})
        assert contract.state == "draft" and not contract.producer_signed_by

    def test_the_active_signature_cannot_be_cleared_afterwards(self, env, officer, officer_b):
        entity = _entity(env, "warehouse.fact_guard_signed")
        contract = (
            env["fix.data.contract"]
            .with_user(officer)
            .create(
                {
                    "dataset_code": "sales.guard.signed",
                    "name": "guard",
                    "entity_id": entity.id,
                    "producer": "order service team",
                    "producer_signatory_id": officer.id,
                    "schema_version": "1.0",
                }
            )
        )
        contract.with_user(officer).action_producer_sign()
        contract.with_user(officer).action_request_approval()
        _decide(contract, officer_b)
        assert contract.state == "active"
        with pytest.raises(ValidationError, match="UNSIGNED"), env.cr.savepoint():
            contract.sudo().write({"producer_signed_by": False})
        assert contract.state == "active" and contract.producer_signed_by == officer

    def test_a_passing_rule_needs_a_recorded_result(self, env, officer):
        entity = _entity(env, "warehouse.fact_guard_rule")
        rule = (
            env["fix.data.quality.rule"]
            .with_user(officer)
            .create({"name": "guard", "entity_id": entity.id, "threshold": 95.0})
        )
        for state in ("passing", "failing"):
            with pytest.raises(ValidationError, match="recorded"), env.cr.savepoint():
                rule.with_user(officer).write({"state": state})
        with pytest.raises(ValidationError, match="recorded"), env.cr.savepoint():
            env["fix.data.quality.rule"].with_user(officer).create(
                {"name": "born green", "entity_id": entity.id, "state": "passing"}
            )
        assert rule.state == "untested" and not rule.last_checked

    def test_the_governed_paths_still_reach_their_states(self, env, officer, officer_b):
        """The guards refuse the shortcut, not the route: a metric still
        publishes through steward review and a decided M63 task, a contract
        still activates on both signatures, a rule still passes on a result."""
        definition = (
            env["fix.metric.definition"]
            .with_user(officer)
            .create({"code": "MET-GUARD-OK", "name": "x", "definition": "a / b"})
        )
        version = (
            env["fix.metric.version"]
            .with_user(officer)
            .create({"definition_id": definition.id, "definition_text": "a / b"})
        )
        version.with_user(officer).action_steward_review()
        version.with_user(officer).action_request_approval()
        _decide(version, officer_b)
        assert (definition.state, definition.current_version_id) == ("published", version)

        entity = _entity(env, "warehouse.fact_guard_ok")
        contract = (
            env["fix.data.contract"]
            .with_user(officer)
            .create(
                {
                    "dataset_code": "sales.guard.ok",
                    "name": "guard",
                    "entity_id": entity.id,
                    "producer": "order service team",
                    "producer_signatory_id": officer.id,
                    "schema_version": "1.0",
                }
            )
        )
        contract.with_user(officer).action_producer_sign()
        contract.with_user(officer).action_request_approval()
        _decide(contract, officer_b)
        assert (contract.state, contract.producer_signed_by) == ("active", officer)

        rule = (
            env["fix.data.quality.rule"]
            .with_user(officer)
            .create({"name": "guard ok", "entity_id": entity.id, "threshold": 95.0})
        )
        rule.with_user(officer).action_check(97.5)
        assert (rule.state, rule.last_measured) == ("passing", False)


class TestSeedResidueRepair:
    """A3-F04: the explicit, logged, idempotent repair of the seeded estate."""

    def test_the_repair_returns_the_live_estate_to_truth(self, env, officer, officer_b):
        hub = live_residue(env)
        counts = repair(env)

        # a. five definitions "published" with no version -> draft
        assert counts["metric_definitions_drafted"] == 5
        assert not env["fix.metric.definition"].search([("state", "=", "published")])
        assert len(env["fix.metric.definition"].search([])) == 5  # nothing deleted

        # b. three contracts "active" without the producer signature -> draft
        assert counts["contracts_unsigned_to_draft"] == 3
        assert not env["fix.data.contract"].search([("state", "=", "active")])
        assert len(env["fix.data.contract"].search([])) == 3

        # c. four pipeline stamps no run produced -> cleared
        assert counts["pipeline_stamps_cleared"] == 4
        assert not env["fix.data.pipeline"].search(
            ["|", ("last_run_at", "!=", False), ("last_success_at", "!=", False)]
        )

        # d. three rules "passing" never measured -> Not yet tested, result cleared
        assert counts["rules_unmeasured"] == 3
        rules = env["fix.data.quality.rule"].search([])
        assert set(rules.mapped("state")) == {"untested"}
        assert not any(rules.mapped("last_checked")) and not any(rules.mapped("last_result"))

        # e. the entity mapping (the obvious technical part)
        assert counts["entities_modelled"] == 3
        models = {e.name: e.res_model for e in env["fix.data.entity"].search([])}
        assert models["Service Orders Table"] == "fix.service.order"
        assert models["Customer API Resource"] == "res.partner"
        assert models["Identity Documents"] == "fix.identity.document"
        assert not models["Order Events Stream"] and not models["SLA Attainment KPI"]
        assert counts["entities_created"] == 3
        for name, kind, model_name, owner, classification in (
            ("AR invoice ledger", "table", "fix.ar.invoice", "Finance (M20)", "confidential"),
            ("Inventory snapshot", "table", "fix.stock.onhand", "Supply Chain (M15)", "internal"),
            ("bKash settlement files", "file", False, "Treasury (M50)", "confidential"),
        ):
            entity = env["fix.data.entity"].search([("name", "=", name)], limit=1)
            assert entity, name
            assert (entity.entity_type, entity.res_model, entity.owner_module) == (
                kind,
                model_name,
                owner,
            )
            assert entity.classification == classification
            assert entity.company_id == hub.company_id
            assert "Repaired by action_repair_seed_residue" in (entity.description or "")

        pipelines = {p.code: p.target_entity_id.name for p in env["fix.data.pipeline"].search([])}
        assert pipelines == {
            "PL-SO-CDC": "Service Orders Table",
            "PL-INV-DAILY": "Inventory snapshot",
            "PL-AR-INCR": "AR invoice ledger",
            "PL-BKASH": "bKash settlement files",
        }
        assert counts["pipelines_repointed"] == 4
        contracts = {c.dataset_code: c.entity_id.name for c in env["fix.data.contract"].search([])}
        assert contracts == {
            "DS-SERVICE-ORDER": "Order Events Stream",
            "DS-AR-INVOICE": "AR invoice ledger",
            "DS-INVENTORY-SNAP": "Inventory snapshot",
        }
        assert counts["contracts_repointed"] == 3

        # e3. two rules re-pointed; the party rule keeps its entity and gets the
        # unique key the party master designates; two stay visibly unmeasurable
        by_name = {r.name: r for r in env["fix.data.quality.rule"].search([])}
        assert counts["rules_repointed"] == 2 and counts["rules_check_field_set"] == 1
        assert by_name["Orders Complete"].entity_id.name == "Service Orders Table"
        assert not by_name["Orders Complete"].check_field
        assert "no check field" in by_name["Orders Complete"].measure_blocker
        assert by_name["Customer Unique"].entity_id.name == "Customer API Resource"
        assert by_name["Customer Unique"].check_field == "legacy_reference"
        assert by_name["Customer Unique"].measure_blocker is False
        assert by_name["Events Fresh"].entity_id.name == "Order Events Stream"
        assert "maps to no Odoo model" in by_name["Events Fresh"].measure_blocker
        for rule in by_name.values():
            assert any(
                "Repaired by action_repair_seed_residue" in (message.body or "")
                for message in rule.message_ids
            ), rule.name

        # f. the prose purge rules state a disposition; the Selection now says so
        assert counts["dispositions_derived"] == 4
        assert counts["policy_currencies_set"] == 4
        by_entity = {
            p.entity_id.name: p.disposition for p in env["fix.data.retention.policy"].search([])
        }
        assert by_entity == {
            "Service Orders Table": "archive",
            "Customer API Resource": "archive",
            "Order Events Stream": "archive",
            "Identity Documents": "pseudonymise",
        }
        # money carries a currency after the repair
        assert all(p.currency_id for p in env["fix.data.retention.policy"].search([]))

    def test_a_second_call_changes_nothing(self, env, officer):
        live_residue(env)
        repair(env)
        snapshot = residue_snapshot(env)
        again = repair(env)
        for key, value in again.items():
            assert value == 0, (key, value, again)
        assert residue_snapshot(env) == snapshot

    def test_it_refuses_a_plain_user(self, env, make_user):
        live_residue(env)
        plain = make_user()
        with pytest.raises(UserError, match="Data Governance Officer"), env.cr.savepoint():
            repair(env(user=plain))
        # and nothing moved
        assert env["fix.metric.definition"].search_count([("state", "=", "published")]) == 5

    def test_it_is_a_doa_administrators_act_too(self, env, make_user):
        live_residue(env)
        doa = make_user(DOA_ADMIN)
        counts = env["fix.data.entity"].with_user(doa).action_repair_seed_residue()
        assert counts["metric_definitions_drafted"] == 5


class TestRetentionDisposition:
    """A3-F10: the purge honours a Selection, not a lowercase comparison of
    free text — and only Delete deletes."""

    def _policy(self, env, officer, disposition, **vals):
        entity = _entity(env, "warehouse.fact_disposition_%s" % disposition)
        # Every probe policy counts the lineage register: its rows CAN be
        # unlinked (quality-test evidence cannot — deletion is refused by the
        # evidence model itself), so a delete policy has a real candidate and
        # the other dispositions have something they must NOT delete.
        entity.write({"res_model": "fix.data.lineage"})
        base = {
            "name": "disposition %s" % disposition,
            "entity_id": entity.id,
            "retention_months": 1,
            "disposition": disposition,
        }
        base.update(vals)
        return env["fix.data.retention.policy"].with_user(officer).create(base)

    def test_the_disposition_is_derived_from_the_prose_rule(self, env, officer):
        for text, expected in (
            ("archive after 36 months", "archive"),
            ("retain 7 years (tax), then archive", "archive"),
            ("retain 7 years, then pseudonymise", "pseudonymise"),
            ("delete the records", "delete"),
            ("retain 7 years", "retain"),  # states no end act: the default
        ):
            policy = (
                env["fix.data.retention.policy"]
                .with_user(officer)
                .create(
                    {
                        "name": text,
                        "entity_id": _entity(env, "warehouse.fact_prose_%s" % expected).id,
                        "retention_months": 36,
                        "purge_rule": text,
                    }
                )
            )
            assert policy.disposition == expected, text

    def test_only_delete_deletes(self, env, officer):
        # an entity whose table holds rows older than the cutoff: a real
        # candidate, proven by the eligible count
        source = _entity(env, "purge source")
        target = _entity(env, "purge target")
        edge = env["fix.data.lineage"].create(
            {"name": "ageing edge", "source_entity_id": source.id, "target_entity_id": target.id}
        )
        env.cr.execute(
            "UPDATE fix_data_lineage SET create_date = now() - interval '10 years' WHERE id = %s",
            (edge.id,),
        )
        env.invalidate_all()

        policy = self._policy(env, officer, "delete", retention_months=12)
        assert policy.purge_rule in (False, "")
        evidence = policy.with_user(officer).action_purge()
        assert evidence.action == "purged" and evidence.purged >= 1
        assert not env["fix.data.lineage"].browse(edge.id).exists()

        for disposition in ("archive", "pseudonymise", "retain"):
            policy = self._policy(env, officer, disposition)
            before = env["fix.data.lineage"].search_count([])
            evidence = policy.with_user(officer).action_purge()
            assert evidence.purged == 0 and evidence.action in ("reported", "eligible")
            assert env["fix.data.lineage"].search_count([]) == before, disposition

    def test_a_live_prose_policy_cannot_delete(self, env, officer):
        """The four live sentences state archive/pseudonymise; after the repair
        none of them may delete, however many records are past retention."""
        live_residue(env)
        repair(env)
        policy = env["fix.data.retention.policy"].search(
            [("entity_id.name", "=", "Identity Documents")]
        )
        assert policy.disposition == "pseudonymise"
        evidence = policy.with_user(officer).action_purge()
        assert evidence.purged == 0 and evidence.action == "reported"


class TestRuleStatesAndMeasurement:
    """A3-F04/F06: a rule nothing has measured is Not yet tested, the reason
    the runner cannot measure a rule is stated once, and the hourly cron
    says what it skipped instead of dropping it in silence."""

    def _rule(self, env, officer, entity, **vals):
        base = {"name": "probe", "entity_id": entity.id, "threshold": 95.0}
        base.update(vals)
        return env["fix.data.quality.rule"].with_user(officer).create(base)

    def test_a_rule_is_born_not_yet_tested_never_passing(self, env, officer):
        entity = _entity(env, "warehouse.fact_born_probe")
        rule = self._rule(env, officer, entity)
        assert (rule.state, rule.last_checked, rule.last_measured) == ("untested", False, False)

    def test_the_blocker_names_the_one_thing_that_stops_the_runner(self, env, officer):
        unmapped = _entity(env, "warehouse.fact_unmapped")
        mapped = _entity(env, "warehouse.fact_mapped", res_model="fix.data.quality.test")
        no_model = self._rule(env, officer, unmapped, check_field="note")
        assert "maps to no Odoo model" in no_model.measure_blocker
        no_field = self._rule(env, officer, mapped, rule_type="completeness")
        assert "no check field" in no_field.measure_blocker
        # the capture form already refuses an unknown column; a seeded rule (or
        # a model that lost the column later) is the only way to reach this
        bad_column = self._rule(env, officer, mapped, check_field="note")
        _sql(
            env,
            "UPDATE fix_data_quality_rule SET check_field = 'no_such_column' WHERE id = %s",
            (bad_column.id,),
        )
        bad_column.invalidate_recordset()
        assert "no column 'no_such_column'" in bad_column.measure_blocker
        human = self._rule(env, officer, mapped, rule_type="accuracy", check_field="note")
        assert "measured by people" in human.measure_blocker
        measurable = self._rule(env, officer, mapped, rule_type="completeness", check_field="note")
        assert measurable.measure_blocker is False
        for blocked in (no_model, no_field, bad_column, human):
            with (
                pytest.raises(UserError, match=re.escape(blocked.measure_blocker)),
                env.cr.savepoint(),
            ):
                blocked.with_user(officer).action_measure()
        assert not env["fix.data.quality.test"].search([("rule_id", "in", blocked.ids)])

    def test_timeliness_measures_the_named_timestamp_not_the_row_edit(self, env, officer):
        seed_entity = _entity(env, "fix_dqt_timeliness_seed", res_model="fix.data.quality.test")
        seed_rule = self._rule(env, officer, seed_entity)
        rows = env["fix.data.quality.test"]
        stale = fields.Datetime.now() - datetime.timedelta(days=3)
        for _ in range(3):
            rows.create({"rule_id": seed_rule.id, "observed_value": 0.0, "checked_at": stale})
        rows.create({"rule_id": seed_rule.id, "observed_value": 0.0})  # checked now
        entity = _entity(env, "fix_dqt_timeliness", res_model="fix.data.quality.test")
        rule = self._rule(
            env,
            officer,
            entity,
            rule_type="timeliness",
            check_field="checked_at",
            freshness_window_hours=24,
            threshold=50.0,
        )
        # every row was written a moment ago (write_date is 'fresh'); only ONE
        # of the four was checked inside the window: 25%, below the 50% bar
        rule.with_user(officer).action_measure()
        assert (rule.last_result, rule.state, rule.last_measured) == (25.0, "failing", True)

    def test_a_timeliness_rule_needs_a_timestamp_column(self, env, officer):
        entity = _entity(env, "fix_dqt_timeliness_text", res_model="fix.data.quality.test")
        rule = self._rule(env, officer, entity, rule_type="timeliness", check_field="note")
        assert "date or datetime column" in rule.measure_blocker
        with pytest.raises(UserError, match="date or datetime column"), env.cr.savepoint():
            rule.with_user(officer).action_measure()

    def test_the_cron_measures_what_it_can_and_says_what_it_skipped(self, env, officer, caplog):
        entity = _entity(env, "fix_dqt_cron", res_model="fix.data.quality.test")
        measurable = self._rule(
            env,
            officer,
            entity,
            name="cron measurable",
            rule_type="completeness",
            check_field="note",
        )
        env["fix.data.quality.test"].create(
            {"rule_id": measurable.id, "observed_value": 0.0, "note": "filled"}
        )
        skipped = [
            self._rule(env, officer, entity, name="cron %s" % kind, **vals)
            for kind, vals in (
                ("no field", {"rule_type": "completeness"}),
                ("accuracy", {"rule_type": "accuracy", "check_field": "note"}),
            )
        ]
        with caplog.at_level(logging.WARNING, logger=RULE_LOG.name):
            result = env["fix.data.quality.rule"]._cron_run_checks()
        assert result == {"measured": 1, "skipped": 2}
        # the measurable rule left a MEASURED evidence row; the others left none
        rows = env["fix.data.quality.test"].search([("rule_id", "in", measurable.ids)])
        assert len(rows) == 2 and rows.filtered(lambda t: t.measured)
        for rule in skipped:
            assert not env["fix.data.quality.test"].search([("rule_id", "=", rule.id)])
            assert rule.state == "untested"
        skipped_lines = [r.getMessage() for r in caplog.records if "SKIPPED" in r.getMessage()]
        assert len(skipped_lines) == 2
        assert all(
            any(rule.name in line and rule.measure_blocker in line for line in skipped_lines)
            for rule in skipped
        )
