"""R01-AUDIT: the D-030 annual licence audit derives its rows from the
register and checks each condition against the infra/ manifests - no
hard-coded "VERIFIED" rows, no unconditional APPROVED."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "run_license_register_audit.py"


def _load():
    spec = importlib.util.spec_from_file_location("run_license_register_audit_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


REGISTER = textwrap.dedent(
    """
    schema: 1000fix-erp/licence-register/1
    review_cadence: annual (D-030)
    components:
      - name: grafana
        licence: AGPL-3.0-and-later
        status: approved-with-condition
        condition: internal operational monitoring only
      - name: tempo
        licence: AGPL-3.0-and-later
        status: approved-with-condition
        condition: same class as grafana
      - name: rustdesk
        licence: AGPL-3.0-and-later
        status: approved-with-condition
        condition: self-hosted only
      - name: redis
        licence: BSD-3-Clause
        status: approved-with-condition
        condition: pinned 7.2.x pending D-031
      - name: hashicorp/vault
        licence: BUSL-1.1
        status: not-approved
        condition: use OpenBao instead
      - name: openbao
        licence: MPL-2.0
        status: approved
    """
)

COMPOSE = textwrap.dedent(
    """
    services:
      grafana:
        image: grafana/grafana:11.6.0@sha256:abc
        ports: ["127.0.0.1:3002:3000"]
      tempo:
        image: grafana/tempo:2.7.0
        ports:
          - "3200:3200"
      redis:
        image: redis:7.2.5
      vault:
        image: openbao/openbao:2.0.0
    """
)


class TestLicenceRegisterAudit(unittest.TestCase):
    def setUp(self):
        self.lic = _load()
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.register = root / "register.yaml"
        self.register.write_text(REGISTER, encoding="utf-8")
        self.infra = root / "infra"
        (self.infra / "compose").mkdir(parents=True)
        self.compose = self.infra / "compose" / "docker-compose.yml"
        self.compose.write_text(COMPOSE, encoding="utf-8")
        # relative_to(REPO_ROOT) in scan_deployments needs the files under it
        self.lic.REPO_ROOT = root

    def tearDown(self):
        self.tmp.cleanup()

    def _rows(self, audit):
        return {r["component"]: r for r in audit["condition_details"]}

    def test_rows_are_derived_from_the_register(self):
        audit = self.lic.audit_license_register(self.register, self.infra)
        rows = self._rows(audit)
        self.assertEqual(sorted(rows), ["grafana", "hashicorp/vault", "redis", "rustdesk", "tempo"])
        self.assertEqual(audit["register_components"], 6)
        self.assertEqual(rows["grafana"]["compliance"], "COMPLIANT")
        self.assertEqual(rows["redis"]["compliance"], "COMPLIANT")
        self.assertEqual(rows["hashicorp/vault"]["compliance"], "COMPLIANT")
        # a condition on use cannot be breached by a component nothing deploys
        self.assertEqual(rows["rustdesk"]["compliance"], "NOT_DEPLOYED")
        self.assertEqual(audit["conditions_not_deployed"], 1)
        # "same class as grafana" inherits grafana's condition; tempo is exposed
        self.assertEqual(rows["tempo"]["compliance"], "NON_COMPLIANT")
        self.assertIn("3200:3200", rows["tempo"]["evidence"])
        self.assertEqual(audit["status"], "FAIL")

    def test_not_approved_component_deployed_is_non_compliant(self):
        self.compose.write_text(
            COMPOSE.replace("openbao/openbao:2.0.0", "hashicorp/vault:1.18.1"), encoding="utf-8"
        )
        rows = self._rows(self.lic.audit_license_register(self.register, self.infra))
        self.assertEqual(rows["hashicorp/vault"]["compliance"], "NON_COMPLIANT")

    def test_version_pin_is_measured(self):
        self.compose.write_text(COMPOSE.replace("redis:7.2.5", "redis:7.4.0"), encoding="utf-8")
        rows = self._rows(self.lic.audit_license_register(self.register, self.infra))
        self.assertEqual(rows["redis"]["compliance"], "NON_COMPLIANT")

    def test_not_deployed_does_not_block_approval(self):
        compliant = COMPOSE.replace('- "3200:3200"', '- "127.0.0.1:3200:3200"')
        self.compose.write_text(compliant, encoding="utf-8")
        audit = self.lic.audit_license_register(self.register, self.infra)
        self.assertEqual(audit["conditions_non_compliant"], 0)
        self.assertEqual(audit["conditions_unmeasured"], 0)
        self.assertEqual(audit["conditions_not_deployed"], 1)  # rustdesk
        self.assertEqual(audit["status"], "APPROVED")

    def test_deployed_component_without_probe_is_unmeasured(self):
        register = REGISTER + textwrap.indent(
            textwrap.dedent(
                """
                - name: meshcentral
                  licence: Apache-2.0
                  status: approved-with-condition
                  condition: preferred arm where choice is neutral
                """
            ),
            "  ",
        )
        self.register.write_text(register, encoding="utf-8")
        compliant = COMPOSE.replace('- "3200:3200"', '- "127.0.0.1:3200:3200"')
        compose = compliant + "  mesh:\n    image: ghcr.io/ylianst/meshcentral:1.1.60\n"
        self.compose.write_text(compose, encoding="utf-8")
        audit = self.lic.audit_license_register(self.register, self.infra)
        self.assertEqual(self._rows(audit)["meshcentral"]["compliance"], "UNMEASURED")
        self.assertEqual(audit["status"], "INCOMPLETE")

    def test_verdict_requires_gate_and_register(self):
        green = {"is_green": True}
        approved = {"status": "APPROVED"}
        retained = [{"retained": True}]
        self.assertEqual(self.lic.compute_verdict(green, approved, retained), "PASS")
        self.assertEqual(self.lic.compute_verdict({"is_green": False}, approved, retained), "FAIL")
        self.assertEqual(self.lic.compute_verdict(green, {"status": "FAIL"}, retained), "FAIL")
        self.assertEqual(
            self.lic.compute_verdict(green, {"status": "INCOMPLETE"}, retained), "INCOMPLETE"
        )
        self.assertEqual(
            self.lic.compute_verdict(green, approved, [{"retained": False}]), "INCOMPLETE"
        )
        # a component without a licence on record cannot be classified
        self.assertEqual(
            self.lic.compute_verdict(green, approved, retained, {"licence_unclassified": 1}),
            "INCOMPLETE",
        )
        self.assertEqual(
            self.lic.compute_verdict(green, approved, retained, {"licence_unclassified": 0}),
            "PASS",
        )

    def test_port_exposure_parsing(self):
        exposed = self.lic._publishes_beyond_loopback
        self.assertFalse(exposed("127.0.0.1:3002:3000"))
        self.assertFalse(exposed("[::1]:3002:3000"))
        self.assertTrue(exposed("3002:3000"))
        self.assertTrue(exposed("3000"))
        self.assertTrue(exposed("0.0.0.0:3002:3000"))
        self.assertFalse(exposed({"target": 3000, "published": 3002, "host_ip": "127.0.0.1"}))
        self.assertTrue(exposed({"target": 3000, "published": 3002}))


TIMESCALE_REGISTER = textwrap.dedent(
    """
    schema: 1000fix-erp/licence-register/1
    review_cadence: annual (D-030)
    components:
      - name: timescaledb
        licence: Apache-2.0/TSL dual
        status: approved-with-condition
        condition: Apache-2.0-licensed features ONLY; TSL features must never be enabled
    """
)

HYPERTABLE_SQL = textwrap.dedent(
    """
    CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
    SELECT create_hypertable('t', 'time', if_not_exists => TRUE);
    """
)


class TestTimescaleProbe(unittest.TestCase):
    def setUp(self):
        self.lic = _load()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.lic.REPO_ROOT = self.root
        self.register = self.root / "register.yaml"
        self.register.write_text(TIMESCALE_REGISTER, encoding="utf-8")
        self.infra = self.root / "infra"
        (self.infra / "compose").mkdir(parents=True)
        self.compose = self.infra / "compose" / "docker-compose.yml"
        self.compose.write_text("services:\n  db:\n    image: postgres:17.4\n", encoding="utf-8")
        self.sql = self.root / "migrations" / "sql" / "telemetry.sql"
        self.sql.parent.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _row(self):
        audit = self.lic.audit_license_register(self.register, self.infra)
        return audit, audit["condition_details"][0]

    def test_unused_extension_is_not_deployed(self):
        audit, row = self._row()
        self.assertEqual(row["compliance"], "NOT_DEPLOYED")
        self.assertEqual(audit["status"], "APPROVED")

    def test_extension_use_without_apache_licence_setting_is_non_compliant(self):
        self.sql.write_text(HYPERTABLE_SQL, encoding="utf-8")
        audit, row = self._row()
        self.assertEqual(row["compliance"], "NON_COMPLIANT")
        self.assertIn("timescaledb.license=apache is not set", row["evidence"])
        self.assertIn("migrations/sql/telemetry.sql (extension)", row["deployments"])
        self.assertEqual(audit["status"], "FAIL")

    def test_tsl_features_are_non_compliant_even_with_apache_setting(self):
        self.compose.write_text(
            "services:\n  db:\n    image: postgres:17.4\n"
            '    command: ["postgres", "-c", "timescaledb.license=apache"]\n',
            encoding="utf-8",
        )
        self.sql.write_text(
            HYPERTABLE_SQL
            + "ALTER TABLE t SET (timescaledb.compress);\n"
            + "SELECT add_retention_policy('t', INTERVAL '90 days');\n",
            encoding="utf-8",
        )
        _, row = self._row()
        self.assertEqual(row["compliance"], "NON_COMPLIANT")
        self.assertIn("native compression", row["evidence"])
        self.assertIn("retention policy", row["evidence"])
        self.assertNotIn("is not set", row["evidence"])

    def test_apache_only_use_is_compliant(self):
        self.compose.write_text(
            "services:\n  db:\n    image: postgres:17.4\n"
            '    command: ["postgres", "-c", "timescaledb.license=apache"]\n',
            encoding="utf-8",
        )
        self.sql.write_text(HYPERTABLE_SQL, encoding="utf-8")
        audit, row = self._row()
        self.assertEqual(row["compliance"], "COMPLIANT")
        self.assertEqual(audit["status"], "APPROVED")

    def test_sql_licence_guard_satisfies_the_probe_when_no_timescale_server_is_deployed(self):
        guard = (
            "DO $$ BEGIN IF coalesce(current_setting('timescaledb.license', true), '') "
            "<> 'apache' THEN RAISE EXCEPTION 'D-030'; END IF; END $$;\n"
        )
        self.sql.write_text(
            "-- comments may name add_retention_policy( or timescaledb.compress freely\n"
            + HYPERTABLE_SQL
            + guard
            + "SELECT drop_chunks('t', older_than => INTERVAL '90 days');\n",
            encoding="utf-8",
        )
        audit, row = self._row()
        self.assertEqual(row["compliance"], "COMPLIANT", row["evidence"])
        self.assertIn("refuses any server", row["evidence"])
        self.assertEqual(audit["status"], "APPROVED")

    def test_guard_does_not_excuse_tsl_calls(self):
        guard = (
            "DO $$ BEGIN IF current_setting('timescaledb.license', true) <> 'apache' "
            "THEN RAISE EXCEPTION 'x'; END IF; END $$;\n"
        )
        self.sql.write_text(
            HYPERTABLE_SQL + guard + "SELECT add_retention_policy('t', INTERVAL '9 days');\n",
            encoding="utf-8",
        )
        _, row = self._row()
        self.assertEqual(row["compliance"], "NON_COMPLIANT")
        self.assertIn("retention policy", row["evidence"])

    def test_committed_telemetry_sql_is_apache_only(self):
        sql = (REPO_ROOT / "migrations" / "sql" / "timescaledb_telemetry_hypertable.sql").read_text(
            encoding="utf-8"
        )
        code = self.lic._strip_sql_comments(sql)
        for feature, rx in self.lic.TSL_FEATURES.items():
            self.assertIsNone(rx.search(code), feature)
        self.assertRegex(code, self.lic.TSL_LICENCE_GUARD)

    def test_test_and_vendor_sources_do_not_count_as_use(self):
        for sub in ("tests", "vendor"):
            path = self.root / sub / "x.sql"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(HYPERTABLE_SQL, encoding="utf-8")
        _, row = self._row()
        self.assertEqual(row["compliance"], "NOT_DEPLOYED")


class TestSbomFromManifests(unittest.TestCase):
    def setUp(self):
        self.lic = _load()
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.lic.REPO_ROOT = root
        self.lic.SBOM_PATH = root / "sbom.cdx.json"
        self.lic.UV_LOCK = root / "uv.lock"
        self.lic.CURRENCY_PATH = root / "missing-components.json"
        (root / "pyproject.toml").write_text(
            '[project]\nname = "demo"\nversion = "1.2.3"\n', encoding="utf-8"
        )
        self.lic.UV_LOCK.write_text(
            textwrap.dedent(
                """
                version = 1
                [[package]]
                name = "demo"
                version = "1.2.3"
                source = { editable = "." }

                [[package]]
                name = "pyyaml"
                version = "6.0.3"
                source = { registry = "https://pypi.org/simple" }

                [[package]]
                name = "zz-not-installed-anywhere"
                version = "0.0.1"
                source = { registry = "https://pypi.org/simple" }
                """
            ),
            encoding="utf-8",
        )
        web = root / "apps" / "web"
        web.mkdir(parents=True)
        (web / "package-lock.json").write_text(
            json.dumps(
                {
                    "lockfileVersion": 3,
                    "packages": {
                        "": {"name": "web"},
                        "node_modules/react": {"version": "19.0.0", "license": "MIT"},
                        "node_modules/mystery": {"version": "1.0.0"},
                    },
                }
            ),
            encoding="utf-8",
        )
        (root / "node_modules" / "x").mkdir(parents=True)
        (root / "node_modules" / "x" / "package-lock.json").write_text(
            json.dumps({"packages": {"node_modules/ignored": {"version": "9"}}}), encoding="utf-8"
        )
        self.reg = {
            "schema": "1000fix-erp/licence-register/1",
            "components": [{"name": "grafana", "licence": "AGPL-3.0-and-later", "status": "x"}],
        }
        self.deployments = [
            {
                "file": "infra/compose/c.yml",
                "service": "grafana",
                "repo": "grafana/grafana",
                "tag": "11.6.0",
                "digest": "",
                "exposed_ports": [],
                "text": "",
            },
            {
                "file": "infra/compose/c.yml",
                "service": "mail",
                "repo": "axllent/mailpit",
                "tag": "",
                "digest": "sha256:abc",
                "exposed_ports": [],
                "text": "",
            },
        ]

    def tearDown(self):
        self.tmp.cleanup()

    def test_components_come_from_the_manifests(self):
        sbom = self.lic.generate_renewed_cyclonedx_sbom(self.reg, self.deployments)
        by_name = {c["name"]: c for c in sbom["components"]}
        self.assertNotIn("demo", by_name)  # the project itself is metadata, not a dependency
        self.assertEqual(by_name["pyyaml"]["version"], "6.0.3")
        self.assertTrue(by_name["pyyaml"]["licenses"])  # installed: metadata read
        self.assertEqual(by_name["zz-not-installed-anywhere"]["licenses"], [])
        self.assertEqual(by_name["react"]["licenses"], ["MIT"])
        self.assertEqual(by_name["mystery"]["licenses"], [])
        self.assertNotIn("ignored", by_name)  # node_modules lockfiles are not manifests
        self.assertEqual(by_name["grafana"]["licenses"], ["AGPL-3.0-and-later"])
        self.assertEqual(by_name["axllent/mailpit"]["version"], "sha256:abc")
        self.assertEqual(sbom["metadata"]["component"]["version"], "1.2.3")
        self.assertTrue(self.lic.SBOM_PATH.is_file())

    def test_summary_counts_unclassified_components(self):
        summary = self.lic.sbom_summary(
            self.lic.generate_renewed_cyclonedx_sbom(self.reg, self.deployments)
        )
        self.assertEqual(summary["total_dependencies"], 6)
        self.assertEqual(summary["licence_unclassified"], 3)  # zz, mystery, mailpit
        self.assertEqual(summary["licence_classified"], 3)


if __name__ == "__main__":
    unittest.main()
