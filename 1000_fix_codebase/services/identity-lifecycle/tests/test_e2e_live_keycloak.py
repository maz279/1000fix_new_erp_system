"""OPT-IN end-to-end check against the local compose Keycloak (auth profile, :8080).

Runs only with FIX_E2E_KEYCLOAK=1 and the dev Keycloak reachable (otherwise SKIPS):

    docker compose --env-file .env -f infra/compose/docker-compose.yml \
        --profile core --profile auth up -d keycloak
    FIX_E2E_KEYCLOAK=1 FIX_E2E_EVIDENCE_DIR=services/identity-lifecycle/evidence \
        KEYCLOAK_URL=http://127.0.0.1:8080 KEYCLOAK_REALM=1000fix-dev \
        KEYCLOAK_ADMIN_USER=admin KEYCLOAK_ADMIN_PASSWORD=<.env> \
        python -m pytest services/identity-lifecycle/tests/test_e2e_live_keycloak.py

A synthetic user (DE-09) with an open session and a realm role is created in the
1000fix-dev realm, employee.left is emitted through fix_events, the real service
deprovisions it, and the result is read back from Keycloak; the user is deleted after.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest
from identity_lifecycle import IdentityLifecycle
from keycloak_admin import KeycloakAdminClient, KeycloakConfig

pytestmark = pytest.mark.integration


def _live_config() -> KeycloakConfig:
    if os.environ.get("FIX_E2E_KEYCLOAK") != "1":
        pytest.skip("opt-in: set FIX_E2E_KEYCLOAK=1 with the local compose Keycloak running")
    config = KeycloakConfig.from_env()
    try:
        urllib.request.urlopen(f"{config.base_url}/realms/{config.realm}", timeout=3).close()  # noqa: S310 - local dev URL from env
    except OSError as exc:
        pytest.skip(f"local Keycloak unreachable: {exc}")
    return config


def _login(config: KeycloakConfig, username: str, password: str) -> int:
    """Password grant on the dev realm's built-in admin-cli client -> HTTP status."""
    data = urllib.parse.urlencode(
        {
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": username,
            "password": password,
        }
    ).encode()
    url = f"{config.base_url}/realms/{config.realm}/protocol/openid-connect/token"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=10) as r:  # noqa: S310 - local dev URL from env
            return r.status
    except urllib.error.HTTPError as exc:
        return exc.code


def test_employee_left_disables_a_real_keycloak_account(buses):
    config = _live_config()
    admin = KeycloakAdminClient(config)
    code = f"e2e-{uuid.uuid4().hex[:8]}"
    password = f"synthetic-{uuid.uuid4().hex}"
    admin._call(
        "POST",
        "/users",
        body={
            "username": code,
            "enabled": True,
            "email": f"{code}@local.invalid",
            "emailVerified": True,
            "firstName": "E2E",
            "lastName": "Leaver",
            "attributes": {"employee_code": [code]},
            "credentials": [{"type": "password", "value": password, "temporary": False}],
        },
    )
    [user] = admin.find_users_by_username(code)
    uid = user["id"]
    evidence: dict = {"realm": config.realm, "keycloak_url": config.base_url, "steps": []}
    try:
        _, role = admin._call("GET", "/roles/fix_technician")
        admin._call("POST", f"/users/{uid}/role-mappings/realm", body=[role])
        assert _login(config, code, password) == 200  # opens a real session
        before = {
            "enabled": admin.get_user(uid)["enabled"],
            "sessions": len(admin.user_sessions(uid)),
            "realm_roles": sorted(r["name"] for r in admin.role_mappings(uid)["realmMappings"]),
        }
        assert before["enabled"] is True and before["sessions"] >= 1
        evidence["steps"].append({"step": "provisioned synthetic user", "state": before})

        t0 = time.perf_counter()
        buses["bus"].publish_dual(
            "employee.left",
            "hr.employee",
            990001,
            {"employee_id": 990001, "employee_code": code, "keycloak_user_id": False},
            {"correlation_id": f"corr-{code}"},
        )
        dep = IdentityLifecycle.from_env(
            bus=lambda: buses["bus"], migration=lambda: buses["migration"]
        )
        [outcome] = dep.drain()
        elapsed = round(time.perf_counter() - t0, 3)
        assert (outcome.status, outcome.keycloak_user_id) == ("deprovisioned", uid)

        after = {
            "enabled": admin.get_user(uid)["enabled"],
            "sessions": len(admin.user_sessions(uid)),
            "realm_roles": sorted(
                r["name"] for r in admin.role_mappings(uid).get("realmMappings") or []
            ),
            "login_status_after": _login(config, code, password),
        }
        assert after["enabled"] is False and after["sessions"] == 0
        assert "fix_technician" not in after["realm_roles"]
        assert after["login_status_after"] in (400, 401)  # account disabled
        [confirmation] = [
            r.value
            for r in buses["kafka"].get_topic_records("fix.events.identity")
            if r.value["event_type"] == "identity.deprovisioned"
        ]
        evidence["steps"].append(
            {
                "step": "employee.left consumed and deprovisioned",
                "outcome": outcome.status,
                "elapsed_seconds": elapsed,
                "state": after,
                "confirmation_payload_keys": sorted(confirmation["payload"]),
                "realm_roles_removed": confirmation["payload"]["realm_roles_removed"],
            }
        )
        evidence["verdict"] = "PASS"
    finally:
        admin._call("DELETE", f"/users/{uid}")
    _record("e2e-keycloak-deprovisioning.json", evidence)


def _record(name: str, evidence: dict) -> None:
    target = os.environ.get("FIX_E2E_EVIDENCE_DIR")
    if target:
        evidence["measured_at_utc"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        evidence["kpi"] = "KPI-090 (deprovision <= 1 h) / FR-SEC-027 (joiner automation)"
        Path(target).mkdir(parents=True, exist_ok=True)
        (Path(target) / name).write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


def test_joiner_then_leaver_against_the_real_realm(buses):
    """employee.joined creates the account (attribute kept by the realm user profile,
    no password, UPDATE_PASSWORD), the stored id keys employee.left, which disables it."""
    config = _live_config()
    admin = KeycloakAdminClient(config)
    code = f"E2E-{uuid.uuid4().hex[:6].upper()}"
    employee_id = 990002
    worker = IdentityLifecycle.from_env(
        bus=lambda: buses["bus"], migration=lambda: buses["migration"]
    )
    evidence: dict = {"realm": config.realm, "keycloak_url": config.base_url, "steps": []}
    uid = None
    try:
        _, profile = admin._call("GET", "/users/profile")
        [declared] = [a for a in profile["attributes"] if a["name"] == "employee_code"]
        assert declared["permissions"] == {"view": ["admin"], "edit": ["admin"]}
        evidence["steps"].append(
            {"step": "realm user profile declares employee_code", "attribute": declared}
        )

        t0 = time.perf_counter()
        buses["bus"].publish_dual(
            "employee.joined",
            "hr.employee",
            employee_id,
            {
                "employee_id": employee_id,
                "employee_code": code,
                "primary_role": "fix_technician",  # a role the dev realm defines
                "name": "E2E Joiner",
                "work_email": f"{code.lower()}@local.invalid",
                "joined_date": "2026-10-22",
            },
            {"correlation_id": f"corr-{code}"},
        )
        [joined] = worker.drain()
        assert joined.status == "provisioned", joined.reason
        uid = joined.keycloak_user_id
        user = admin.get_user(uid)
        _, credentials = admin._call("GET", f"/users/{uid}/credentials")
        provisioned = {
            "elapsed_seconds": round(time.perf_counter() - t0, 3),
            "username": user["username"],
            "enabled": user["enabled"],
            "employee_code_attribute": (user.get("attributes") or {}).get("employee_code"),
            "required_actions": user.get("requiredActions"),
            "credentials": len(credentials or []),
            "realm_roles": sorted(r["name"] for r in admin.role_mappings(uid)["realmMappings"]),
            "found_by_attribute_search": [
                u["id"] for u in admin.find_users_by_attribute("employee_code", code)
            ]
            == [uid],
        }
        assert provisioned["enabled"] is True and provisioned["credentials"] == 0
        assert provisioned["employee_code_attribute"] == [code]
        assert provisioned["required_actions"] == ["UPDATE_PASSWORD"]
        assert "fix_technician" in provisioned["realm_roles"]
        assert provisioned["found_by_attribute_search"] is True
        evidence["steps"].append(
            {"step": "employee.joined -> identity provisioned", "state": provisioned}
        )

        # replaying the joiner never creates a second account
        buses["bus"].publish_dual(
            "employee.joined",
            "hr.employee",
            employee_id,
            {"employee_id": employee_id, "employee_code": code},
            {},
        )
        [again] = worker.drain()
        assert (again.status, again.keycloak_user_id) == ("provisioned", uid)
        assert len(admin.find_users_by_attribute("employee_code", code)) == 1
        evidence["steps"].append(
            {"step": "second employee.joined reuses the account", "accounts": 1}
        )

        t1 = time.perf_counter()
        buses["bus"].publish_dual(  # M21 stored the id from identity.provisioned
            "employee.left",
            "hr.employee",
            employee_id,
            {"employee_id": employee_id, "employee_code": code, "keycloak_user_id": uid},
            {"correlation_id": f"corr-{code}"},
        )
        [left] = worker.drain()
        assert (left.status, left.keycloak_user_id) == ("deprovisioned", uid)
        after = admin.get_user(uid)
        deprovisioned = {
            "elapsed_seconds": round(time.perf_counter() - t1, 3),
            "enabled": after["enabled"],
            "sessions": len(admin.user_sessions(uid)),
            "realm_roles": sorted(
                r["name"] for r in admin.role_mappings(uid).get("realmMappings") or []
            ),
        }
        assert deprovisioned["enabled"] is False and deprovisioned["realm_roles"] == []
        evidence["steps"].append(
            {"step": "employee.left (by stored id) -> deprovisioned", "state": deprovisioned}
        )
        emitted = sorted(
            r.value["event_type"] for r in buses["kafka"].get_topic_records("fix.events.identity")
        )
        assert emitted == ["identity.deprovisioned", "identity.provisioned", "identity.provisioned"]
        evidence["events_emitted"] = emitted
        evidence["verdict"] = "PASS"
    finally:
        if uid:
            admin._call("DELETE", f"/users/{uid}")
    _record("e2e-keycloak-joiner-leaver.json", evidence)
