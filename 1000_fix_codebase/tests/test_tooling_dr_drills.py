"""GV-009: the tooling/dr drill runners (run_g5_dr_drill, run_g6_dr_drill,
run_g7_dr_drill, run_g8_full_estate_dr_drill, run_ha_kill_node_drills,
run_telemetry_retention_restore_drill, run_r10_m04_dr_rehearsal) measure the
DR/HA configuration they can read and report every failover / kill / restore
step as UNMEASURED - never a hard-coded PASS, RPO or RTO.

Every module's path constants are pointed at a temporary tree; no test reads
or writes real evidence, touches the network or a database.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DR_DIR = REPO_ROOT / "tooling" / "dr"
RUNBOOK_NAME = "RB-52-dr-disaster-recovery-and-cutover.md"


def _load(stem: str):
    spec = importlib.util.spec_from_file_location(f"{stem}_ut", DR_DIR / f"{stem}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------- fixtures
def _prod() -> dict:
    return {
        "services": {
            "postgres-prod": {
                "image": "postgres:17.4",
                "command": [
                    "postgres",
                    "-c", "wal_level=replica",
                    "-c", "max_wal_senders=10",
                    "-c", "archive_mode=on",
                    "-c", "archive_command=cp %p /wal_archive/%f",
                ],
            }
        }
    }  # fmt: skip


def _dr(bootstrap: bool = True) -> dict:
    service = {
        "image": "postgres:17.4",
        "command": [
            "postgres",
            "-c", "hot_standby=on",
            "-c", "primary_conninfo=host=postgres-prod user=fix_standby",
        ],
        "healthcheck": {"test": ["CMD-SHELL", "psql -tAc 'SELECT pg_is_in_recovery()'"]},
    }  # fmt: skip
    if bootstrap:
        service["entrypoint"] = ["sh", "-c", "pg_basebackup -R -D /data && exec postgres"]
    return {"services": {"postgres-dr": service}}


def _kafka(healthy_check: bool = True) -> dict:
    test = "kafka-cluster.sh cluster-id --bootstrap-server 127.0.0.1:9092"
    if not healthy_check:
        test += " || exit 0"
    return {
        "services": {
            f"kafka-{n}": {
                "image": "apache/kafka:3.8.0",
                "environment": {
                    "KAFKA_NODE_ID": n,
                    "KAFKA_PROCESS_ROLES": "broker,controller",
                    "KAFKA_CONTROLLER_QUORUM_VOTERS": "1@kafka-1:9093,2@kafka-2:9093,3@kafka-3:9093",
                    "KAFKA_DEFAULT_REPLICATION_FACTOR": 3,
                    "KAFKA_MIN_INSYNC_REPLICAS": 2,
                },
                "healthcheck": {"test": ["CMD-SHELL", test]},
            }
            for n in (1, 2, 3)
        }
    }


def _intelligence(clickhouse_volume: bool = True, timescale: bool = True) -> dict:
    services: dict = {"clickhouse": {"image": "clickhouse/clickhouse-server:24.3"}}
    if clickhouse_volume:
        services["clickhouse"]["volumes"] = ["ch-data:/var/lib/clickhouse"]
    if timescale:
        services["timescaledb"] = {"image": "timescale/timescaledb:2.14.2-pg17"}
    return {"services": services}


def _ha(kong_mounted: bool = True) -> dict:
    def node(image: str, **extra) -> dict:
        return {
            "image": image,
            "healthcheck": {"test": ["CMD-SHELL", "probe"]},
            "restart": "unless-stopped",
            **extra,
        }

    kong_volumes = {"volumes": ["./kong/kong.yml:/kong/kong.yml:ro"]} if kong_mounted else {}
    kong_env = {"KONG_DATABASE": "off", "KONG_DECLARATIVE_CONFIG": "/kong/kong.yml"}
    kc_env = {"KC_DB_URL_HOST": "postgres-ha-primary"}
    return {
        "services": {
            "postgres-ha-primary": node(
                "postgres:17.4", command=["postgres", "-c", "wal_level=replica"]
            ),
            "postgres-ha-standby": node(
                "postgres:17.4",
                command=["postgres", "-c", "primary_conninfo=host=postgres-ha-primary"],
                entrypoint=["sh", "-c", "pg_basebackup -R -D /data && exec postgres"],
            ),
            "keycloak-ha-01": node(
                "keycloak:26", command=["start", "--cache=ispn"], environment=kc_env
            ),
            "keycloak-ha-02": node(
                "keycloak:26", command=["start", "--cache=ispn"], environment=kc_env
            ),
            "kong-ha-01": node("kong:3.8", environment=kong_env, **kong_volumes),
            "kong-ha-02": node("kong:3.8", environment=kong_env, **kong_volumes),
            "nginx-ha-01": node("nginx:1.27", volumes=["./nginx:/etc/nginx/conf.d:ro"]),
            "nginx-ha-02": node("nginx:1.27", volumes=["./nginx:/etc/nginx/conf.d:ro"]),
        }
    }


GOOD_DDL = """
-- comments may mention add_retention_policy( or timescaledb.compress freely
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
DO $$
BEGIN
    IF coalesce(current_setting('timescaledb.license', true), '') <> 'apache' THEN
        RAISE EXCEPTION 'D-030';
    END IF;
END
$$;
SELECT create_hypertable('fix_technician_telemetry', 'time');
CREATE OR REPLACE FUNCTION fix_telemetry_apply_retention(
    retain INTERVAL DEFAULT INTERVAL '90 days'
) RETURNS INTEGER LANGUAGE plpgsql AS $$
DECLARE dropped INTEGER;
BEGIN
    SELECT count(*) INTO dropped FROM drop_chunks('fix_technician_telemetry', older_than => retain);
    RETURN dropped;
END
$$;
"""

TSL_DDL = (
    GOOD_DDL
    + """
ALTER TABLE fix_technician_telemetry SET (timescaledb.compress);
SELECT add_retention_policy('fix_technician_telemetry', INTERVAL '90 days');
"""
)

RETENTION_DAG = """
dag = DAG(dag_id="telemetry_retention_daily", schedule="@daily")
RETENTION_SQL = "SELECT fix_telemetry_apply_retention();"
"""

ARCHIVING_DAG = (
    RETENTION_DAG
    + """
archive = PythonOperator(task_id="archive_expiring_chunks", python_callable=archive_chunks)
"""
)


class _TempTree(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="dr_drills_ut_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.compose = self.root / "infra" / "compose"
        self.compose.mkdir(parents=True)
        self.evidence = self.root / "docs" / "traceability" / "evidence"
        self.runbook = self.root / "docs" / "runbooks" / RUNBOOK_NAME
        self.runbook.parent.mkdir(parents=True)
        self.runbook.write_text("# RB-52\n", encoding="utf-8")
        self.write("docker-compose.prod.yml", _prod())
        self.write("docker-compose.dr.yml", _dr())
        self.write("docker-compose.asset-ml.yml", _kafka())
        self.write("docker-compose.intelligence.yml", _intelligence())
        self.write("docker-compose.ha.yml", _ha())

    def write(self, name: str, data: dict) -> None:
        (self.compose / name).write_text(yaml.safe_dump(data), encoding="utf-8")

    def point(self, module) -> None:
        """Aim every path constant the module has at the temporary tree."""
        for attr, value in {
            "COMPOSE_DIR": self.compose,
            "RUNBOOK": self.runbook,
            "EVIDENCE_DIR": self.evidence,
            "TRACEABILITY_DIR": self.root / "docs" / "traceability",
        }.items():
            if hasattr(module, attr):
                setattr(module, attr, value)

    @staticmethod
    def run_main(module) -> int:
        with contextlib.redirect_stdout(io.StringIO()):
            return module.main()


# (script stem, builder, verdict field, path to the RPO value, path to the RTO value)
PG_DRILLS = (
    ("run_g5_dr_drill", "execute_dr_drill", "status", ("sla_metrics", "rpo_achieved_seconds"), ("sla_metrics", "rto_achieved_seconds")),
    ("run_g6_dr_drill", "execute_dr_drill", "overall_status", ("metrics", "rpo_achieved_seconds"), ("metrics", "rto_achieved_seconds")),
    ("run_g7_dr_drill", "execute_dr_drill", "verdict", ("metrics", "rpo_measured_seconds"), ("metrics", "rto_measured_seconds")),
    ("run_g8_full_estate_dr_drill", "execute_full_estate_dr_drill", "verdict", ("measured_metrics", "rpo_measured_seconds"), ("measured_metrics", "rto_measured_seconds")),
    ("run_r10_m04_dr_rehearsal", "execute_dr_rehearsal", "status", ("actual_rpo_seconds",), ("actual_rto_seconds",)),
)  # fmt: skip

CONFIG_IDS = {
    "primary_replication_config",
    "dr_standby_config",
    "runbook_present",
    "kafka_kraft_quorum_config",
    "kafka_healthchecks",
    "clickhouse_persistence",
    "timescaledb_declared",
}


def _dig(data: dict, path: tuple[str, ...]):
    for key in path:
        data = data[key]
    return data


class PostgresDrDrillsTest(_TempTree):
    def build(self, stem: str, builder: str):
        module = _load(stem)
        self.point(module)
        return module, getattr(module, builder)()

    def test_sound_config_is_incomplete_never_pass(self) -> None:
        for stem, builder, field, rpo, rto in PG_DRILLS:
            with self.subTest(stem):
                _, ev = self.build(stem, builder)
                self.assertEqual(ev[field], "INCOMPLETE")
                for check in ev["checks"]:
                    expected = "PASS" if check["id"] in CONFIG_IDS else "UNMEASURED"
                    self.assertEqual(check["status"], expected, check)
                self.assertIsNone(_dig(ev, rpo))
                self.assertIsNone(_dig(ev, rto))

    def test_standby_without_bootstrap_fails(self) -> None:
        self.write("docker-compose.dr.yml", _dr(bootstrap=False))
        for stem, builder, field, _, _ in PG_DRILLS:
            with self.subTest(stem):
                _, ev = self.build(stem, builder)
                self.assertEqual(ev[field], "FAIL")
                standby = next(c for c in ev["checks"] if c["id"] == "dr_standby_config")
                self.assertEqual(standby["status"], "FAIL")
                self.assertIn("standby bootstrap", standby["detail"])

    def test_missing_infra_fails(self) -> None:
        shutil.rmtree(self.compose)
        for stem, builder, field, _, _ in PG_DRILLS:
            with self.subTest(stem):
                _, ev = self.build(stem, builder)
                self.assertEqual(ev[field], "FAIL")

    def test_async_replication_is_reported(self) -> None:
        _, ev = self.build("run_g5_dr_drill", "execute_dr_drill")
        primary = next(c for c in ev["checks"] if c["id"] == "primary_replication_config")
        self.assertIn("asynchronous", primary["detail"])

    def test_always_healthy_kafka_healthcheck_fails(self) -> None:
        self.write("docker-compose.asset-ml.yml", _kafka(healthy_check=False))
        for stem, builder, field, _, _ in PG_DRILLS[1:4]:
            with self.subTest(stem):
                _, ev = self.build(stem, builder)
                self.assertEqual(ev[field], "FAIL")
                hc = next(c for c in ev["checks"] if c["id"] == "kafka_healthchecks")
                self.assertIn("|| exit 0", hc["detail"])

    def test_g8_clickhouse_and_timescale_gaps_fail(self) -> None:
        self.write("docker-compose.intelligence.yml", _intelligence(False, False))
        _, ev = self.build("run_g8_full_estate_dr_drill", "execute_full_estate_dr_drill")
        self.assertEqual(ev["verdict"], "FAIL")
        status = {c["id"]: c["status"] for c in ev["checks"]}
        self.assertEqual(status["clickhouse_persistence"], "FAIL")
        self.assertEqual(status["timescaledb_declared"], "FAIL")
        self.assertIsNone(ev["measured_metrics"]["data_loss_records"])

    def test_main_writes_evidence_and_derives_exit_code(self) -> None:
        for stem, _, field, _, _ in PG_DRILLS:
            with self.subTest(stem):
                module = _load(stem)
                self.point(module)
                self.assertEqual(self.run_main(module), 2)
                written = json.loads((self.evidence / module.EVIDENCE_FILE).read_text("utf-8"))
                self.assertEqual(written[field], "INCOMPLETE")
        self.write("docker-compose.dr.yml", _dr(bootstrap=False))
        for stem, _, field, _, _ in PG_DRILLS:
            with self.subTest(stem):
                module = _load(stem)
                self.point(module)
                self.assertEqual(self.run_main(module), 1)
                written = json.loads((self.evidence / module.EVIDENCE_FILE).read_text("utf-8"))
                self.assertEqual(written[field], "FAIL")

    def test_g8_report_carries_computed_verdict(self) -> None:
        module = _load("run_g8_full_estate_dr_drill")
        self.point(module)
        self.run_main(module)
        report = (self.root / "docs" / "traceability" / module.REPORT_FILE).read_text("utf-8")
        self.assertIn("**`INCOMPLETE`**", report)
        self.assertIn("Not eligible for sign-off", report)
        self.assertNotIn("Certified", report)
        self.assertNotIn("| **PASS** |", report.split("## 2. Checks")[0])


class HaKillNodeDrillsTest(_TempTree):
    def build(self) -> dict:
        module = _load("run_ha_kill_node_drills")
        self.point(module)
        return module.run_all_ha_drills()

    def test_sound_config_kill_drills_unmeasured(self) -> None:
        ev = self.build()
        self.assertEqual(ev["status"], "INCOMPLETE")
        self.assertFalse(ev["all_passed"])
        self.assertIsNone(ev["total_outage_tolerated"])
        for drill in ev["drills"]:
            self.assertEqual(drill["config_check"]["status"], "PASS", drill)
            self.assertEqual(drill["kill_drill"]["status"], "UNMEASURED")

    def test_unmounted_kong_config_fails(self) -> None:
        self.write("docker-compose.ha.yml", _ha(kong_mounted=False))
        ev = self.build()
        self.assertEqual(ev["status"], "FAIL")
        kong = next(d for d in ev["drills"] if d["drill"] == "KILL_KONG_GATEWAY_NODE_1")
        self.assertEqual(kong["config_check"]["status"], "FAIL")

    def test_missing_ha_compose_fails(self) -> None:
        (self.compose / "docker-compose.ha.yml").unlink()
        ev = self.build()
        self.assertEqual(ev["status"], "FAIL")
        self.assertTrue(all(d["config_check"]["status"] == "FAIL" for d in ev["drills"]))

    def test_main_exit_code(self) -> None:
        module = _load("run_ha_kill_node_drills")
        self.point(module)
        self.assertEqual(self.run_main(module), 2)
        written = json.loads((self.evidence / module.EVIDENCE_FILE).read_text("utf-8"))
        self.assertEqual(written["status"], "INCOMPLETE")


class TelemetryRetentionRestoreDrillTest(_TempTree):
    def build(self, ddl: str | None, dag: str | None = RETENTION_DAG) -> tuple[object, dict]:
        module = _load("run_telemetry_retention_restore_drill")
        module.ROOT_DIR = self.root
        module.EVIDENCE_DIR = self.evidence
        module.DDL_PATH = self.root / "migrations" / "sql" / "timescaledb_telemetry_hypertable.sql"
        module.DAGS_DIR = self.root / "dags"
        if ddl is not None:
            module.DDL_PATH.parent.mkdir(parents=True, exist_ok=True)
            module.DDL_PATH.write_text(ddl, encoding="utf-8")
        if dag is not None:
            module.DAGS_DIR.mkdir(parents=True, exist_ok=True)
            (module.DAGS_DIR / "telemetry_retention_dag.py").write_text(dag, encoding="utf-8")
        return module, module.execute_restore_drill()

    @staticmethod
    def status(ev: dict) -> dict:
        return {c["id"]: c["status"] for c in ev["checks"]}

    def test_apache_only_ddl_with_scheduled_retention(self) -> None:
        _, ev = self.build(GOOD_DDL)
        status = self.status(ev)
        self.assertEqual(status["licence_d030"], "PASS")
        self.assertEqual(status["retention_policy"], "PASS")
        self.assertEqual(status["retention_schedule"], "PASS")
        # compression is TSL-only: the requirement cannot be met under D-030
        self.assertEqual(status["compression_policy"], "FAIL")
        self.assertEqual(status["archive_before_drop"], "FAIL")
        self.assertEqual(status["restore_to_staging"], "UNMEASURED")
        self.assertEqual(ev["status"], "FAIL")
        self.assertIsNone(ev["restore_verification"]["restored_records"])
        self.assertIn("not measured", ev["storage_model"]["basis"])

    def test_tsl_features_fail_the_licence_check(self) -> None:
        _, ev = self.build(TSL_DDL)
        licence = next(c for c in ev["checks"] if c["id"] == "licence_d030")
        self.assertEqual(licence["status"], "FAIL")
        self.assertIn("native compression", licence["detail"])
        self.assertIn("retention policy", licence["detail"])

    def test_missing_licence_guard_fails(self) -> None:
        _, ev = self.build(GOOD_DDL.replace("RAISE EXCEPTION 'D-030';", "NULL;"))
        self.assertEqual(self.status(ev)["licence_d030"], "FAIL")

    def test_unscheduled_retention_fails(self) -> None:
        _, ev = self.build(GOOD_DDL, dag=None)
        self.assertEqual(self.status(ev)["retention_schedule"], "FAIL")

    def test_archival_task_satisfies_archive_check(self) -> None:
        _, ev = self.build(GOOD_DDL, dag=ARCHIVING_DAG)
        self.assertEqual(self.status(ev)["archive_before_drop"], "PASS")

    def test_commented_out_retention_does_not_count(self) -> None:
        ddl = GOOD_DDL.replace(
            "CREATE OR REPLACE FUNCTION fix_telemetry_apply_retention(",
            "-- CREATE OR REPLACE FUNCTION fix_telemetry_apply_retention(",
        )
        _, ev = self.build(ddl)
        self.assertEqual(self.status(ev)["retention_policy"], "FAIL")

    def test_committed_ddl_is_apache_only_and_scheduled(self) -> None:
        module = _load("run_telemetry_retention_restore_drill")
        status = self.status(module.execute_restore_drill())
        self.assertEqual(status["licence_d030"], "PASS")
        self.assertEqual(status["retention_policy"], "PASS")
        self.assertEqual(status["retention_schedule"], "PASS")

    def test_missing_ddl_fails_and_exit_code_is_derived(self) -> None:
        module, ev = self.build(None)
        self.assertEqual(ev["status"], "FAIL")
        self.assertEqual(self.run_main(module), 1)
        written = json.loads((self.evidence / module.EVIDENCE_FILE).read_text("utf-8"))
        self.assertEqual(written["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
