"""identity_lifecycle.py — M29 joiner/leaver automation against Keycloak (FR-SEC-027, KPI-090).

M21 (cd_employee_core) emits ``employee.joined`` and ``employee.left`` for the
employee master; this worker applies them to Keycloak and reports the IdP-confirmed
outcome back through fix_events (AS-08):

Joiner (``employee.joined`` -> ``identity.provisioned`` / ``identity.provision_failed``):
  * the identity key is the employee code: the ``employee_code`` user attribute
    (declared admin-only in the realm user profile), username = the employee code;
  * an existing account with that employee code is REUSED, never duplicated (a
    disabled one - a rehire - is re-enabled and must set a new password);
  * a new account is enabled with the required action UPDATE_PASSWORD and NO
    password - the service never sets or knows a credential;
  * "the role from the position profile" (FR-SEC-027): the employee's primary
    role code, which the 05-04 role register maps 1:1 to a Keycloak realm role
    (fix.role.keycloak_role == code); a role missing from the realm is a failure.

Leaver (``employee.left`` -> ``identity.deprovisioned`` / ``identity.deprovision_failed``):
  resolve by the stored Keycloak user id, else the employee code; disable (never
  delete - M29 §8 keeps the identity for audit), revoke sessions, remove every
  realm/client role mapping.

Both flows VERIFY with Keycloak before claiming success (GV-009), are re-delivery
safe (outcome per event_id), retry transient IdP failures with capped exponential
backoff, and report a persistent failure with a reason code.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from keycloak_admin import KeycloakAdminClient, KeycloakConfig, KeycloakError, is_user_id

from libs.py.fix_events import (
    ConsumerGroupMigrationManager,
    DualWriteEventBus,
    get_dual_bus,
    get_migration_manager,
    normalize_bus_event,
)
from libs.py.fix_events.dual_write import payload_digest
from libs.py.fix_events.kafka_bus import map_topic_for_event

logger = logging.getLogger("identity_lifecycle")

JOINED_EVENT_TYPE = "employee.joined"
LEFT_EVENT_TYPE = "employee.left"
EMPLOYEE_TOPIC = map_topic_for_event(LEFT_EVENT_TYPE)
CONSUMER_GROUP = "identity-lifecycle"
EMPLOYEE_AGGREGATE = "hr.employee"
EMPLOYEE_CODE_ATTRIBUTE = "employee_code"
FIRST_LOGIN_ACTION = "UPDATE_PASSWORD"
#: ledger states after which a re-delivered event must not be acted on again
FINAL_STATES = frozenset({"provisioned", "deprovisioned", "permanent_failure"})
_USER_FIELDS = (
    "username",
    "email",
    "emailVerified",
    "firstName",
    "lastName",
    "enabled",
    "attributes",
    "requiredActions",
)


class LifecycleFailure(Exception):
    """A classified, permanent failure: retrying cannot help."""

    reason_code = "lifecycle_failure"

    def __init__(self, message: str, *, reason_code: str | None = None, user_id: str | None = None):
        super().__init__(message)
        self.reason_code = reason_code or self.reason_code
        self.user_id = user_id


class IdentityNotFound(LifecycleFailure):
    reason_code = "identity_not_found"


class AmbiguousIdentity(LifecycleFailure):
    """More than one account matches - never guess which one to change."""

    reason_code = "identity_ambiguous"


@dataclass
class Outcome:
    status: str  # provisioned | deprovisioned | failed | duplicate | ignored
    event_id: str | None = None
    employee_id: int | None = None
    keycloak_user_id: str | None = None
    reason: str | None = None
    attempts: int = 0


class ProcessedLedger:
    """event_id -> outcome; optionally persisted so a restart cannot replay side effects."""

    def __init__(self, path: Path | None = None):
        self.path = path
        self._entries: dict[str, dict[str, Any]] = {}
        if path is not None and path.is_file():
            self._entries = json.loads(path.read_text(encoding="utf-8"))

    def __len__(self) -> int:
        return len(self._entries)

    def get(self, key: str) -> dict[str, Any] | None:
        return self._entries.get(key)

    def record(self, key: str, entry: dict[str, Any]) -> None:
        self._entries[key] = entry
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=".ledger-")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(self._entries, handle, sort_keys=True)
        os.replace(tmp, self.path)  # atomic: a crash never leaves half a ledger


def _utc_now() -> datetime:
    return datetime.now(UTC)


def split_name(name: Any) -> tuple[str, str]:
    """'Rahim Uddin Ahmed' -> ('Rahim', 'Uddin Ahmed'); a single name is the first name."""
    parts = str(name or "").split()
    return (parts[0], " ".join(parts[1:])) if parts else ("", "")


class IdentityLifecycle:
    def __init__(
        self,
        client: KeycloakAdminClient,
        ledger: ProcessedLedger | None = None,
        *,
        max_attempts: int = 4,
        backoff_base: float = 0.5,
        backoff_cap: float = 8.0,
        sleep: Callable[[float], None] = time.sleep,
        now: Callable[[], datetime] = _utc_now,
        bus: Callable[[], DualWriteEventBus] = get_dual_bus,
        migration: Callable[[], ConsumerGroupMigrationManager] = get_migration_manager,
    ):
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        self.client = client
        # `is None`, not `or`: an EMPTY persistent ledger is falsy (len 0) and must be kept
        self.ledger = ledger if ledger is not None else ProcessedLedger()
        self.max_attempts = max_attempts
        self.backoff_base = backoff_base
        self.backoff_cap = backoff_cap
        self._sleep = sleep
        self._now = now
        self._bus = bus
        self._migration = migration
        # event type -> (success status, apply, emit on success, emit on failure)
        self._flows: dict[str, tuple[str, Callable, Callable, Callable]] = {
            JOINED_EVENT_TYPE: (
                "provisioned",
                self._provision,
                self._emit_provisioned,
                self._emit_provision_failed,
            ),
            LEFT_EVENT_TYPE: (
                "deprovisioned",
                self._deprovision,
                self._emit_deprovisioned,
                self._emit_deprovision_failed,
            ),
        }

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None, **kwargs: Any) -> IdentityLifecycle:
        """Fail closed: raises KeycloakConfigError when the admin settings are missing."""
        env = dict(os.environ) if env is None else env
        config = KeycloakConfig.from_env(env)
        ledger_path = (env.get("IDENTITY_LIFECYCLE_LEDGER") or "").strip()
        ledger = ProcessedLedger(Path(ledger_path) if ledger_path else None)
        return cls(KeycloakAdminClient(config), ledger, **kwargs)

    # ------------------------------------------------------------------ consuming

    def drain(self, limit: int = 50) -> list[Outcome]:
        """Consume pending employee events through fix_events (FF-28: no direct bus client)."""
        manager = self._migration()
        manager.register_group(CONSUMER_GROUP)
        outcomes: list[Outcome] = []
        manager.consume_event(
            CONSUMER_GROUP, EMPLOYEE_TOPIC, lambda raw: outcomes.append(self.handle(raw)), limit
        )
        return outcomes

    def handle(self, raw_event: dict[str, Any]) -> Outcome:
        try:
            event = normalize_bus_event(raw_event)
        except ValueError as exc:  # never block the stream on a poisoned message
            logger.error("identity-lifecycle: malformed event skipped: %s", exc)
            return Outcome("ignored", reason=f"malformed event: {exc}")
        flow = self._flows.get(event["event_type"] or "")
        if flow is None:
            return Outcome("ignored", event_id=event["event_id"])
        success_status, apply, emit_success, emit_failure = flow

        payload = event["payload"]
        # Only the employee-master event identifies an employee: an onboarding plan's
        # employee.joined (cd_talent) carries the PLAN id, never use it as one.
        fallback = event["aggregate_id"] if event["aggregate"] == EMPLOYEE_AGGREGATE else None
        try:
            employee_id = int(payload.get("employee_id") or fallback)
        except (TypeError, ValueError):
            return Outcome(
                "ignored",
                event_id=event["event_id"],
                reason=f"{event['event_type']} without an employee id",
            )
        employee_code = str(payload.get("employee_code") or "").strip()
        key = event["event_id"] or f"sha256:{payload_digest(payload)}"
        prior = self.ledger.get(key)
        if prior and prior["status"] in FINAL_STATES:
            return Outcome(
                "duplicate",
                event_id=key,
                employee_id=employee_id,
                keycloak_user_id=prior.get("keycloak_user_id"),
            )

        attempts, permanent, reason_code, reason = 0, False, "", ""
        user_id = (
            payload.get("keycloak_user_id") if is_user_id(payload.get("keycloak_user_id")) else None
        )
        while attempts < self.max_attempts:
            attempts += 1
            try:
                result = apply(payload)
            except LifecycleFailure as exc:
                permanent, reason_code, reason = True, exc.reason_code, str(exc)
                user_id = exc.user_id or user_id
                break
            except KeycloakError as exc:
                reason = str(exc)
                if not exc.transient:
                    permanent, reason_code = True, "idp_rejected"
                    break
                reason_code = "idp_unavailable"
                if attempts < self.max_attempts:
                    self._sleep(min(self.backoff_cap, self.backoff_base * 2 ** (attempts - 1)))
                continue
            user_id = str(result["user"]["id"])
            emit_success(event, employee_id, employee_code, result, attempts)
            self.ledger.record(key, {"status": success_status, "keycloak_user_id": user_id})
            logger.info("identity-lifecycle: %s %s (%s)", employee_code, success_status, user_id)
            return Outcome(
                success_status,
                event_id=key,
                employee_id=employee_id,
                keycloak_user_id=user_id,
                attempts=attempts,
            )

        emit_failure(event, employee_id, employee_code, user_id, reason_code, reason, attempts)
        self.ledger.record(
            key,
            {
                "status": "permanent_failure" if permanent else "transient_failure",
                "reason_code": reason_code,
                "keycloak_user_id": user_id,
            },
        )
        logger.warning(
            "identity-lifecycle: %s %s FAILED: %s", event["event_type"], employee_code, reason
        )
        return Outcome(
            "failed",
            event_id=key,
            employee_id=employee_id,
            keycloak_user_id=user_id,
            reason=f"{reason_code}: {reason}",
            attempts=attempts,
        )

    # ------------------------------------------------------------------ lookups

    def _find_by_code(self, code: str) -> dict[str, Any] | None:
        """The ONE account for an employee code: attribute first, then username."""
        matches = self.client.find_users_by_attribute(EMPLOYEE_CODE_ATTRIBUTE, code)
        if len(matches) > 1:
            raise AmbiguousIdentity(f"{len(matches)} Keycloak accounts carry employee {code}")
        if matches:
            return matches[0]
        by_username = self.client.find_users_by_username(code)
        return by_username[0] if by_username else None

    def _resolve(self, payload: dict[str, Any]) -> dict[str, Any]:
        kc_id = payload.get("keycloak_user_id")
        if is_user_id(kc_id):
            user = self.client.get_user(kc_id)
            if user is not None:
                return user
        code = str(payload.get("employee_code") or "").strip()
        if not code:
            raise IdentityNotFound(
                "employee.left carries neither a known Keycloak user id nor an employee code"
            )
        user = self._find_by_code(code)
        if user is None:
            raise IdentityNotFound(f"no Keycloak account for employee {code}")
        return user

    # ------------------------------------------------------------------ joiner

    def _provision(self, payload: dict[str, Any]) -> dict[str, Any]:
        code = str(payload.get("employee_code") or "").strip()
        if not code:
            raise LifecycleFailure(
                "employee.joined carries no employee code - nothing to key the identity on",
                reason_code="no_employee_code",
            )
        user = self._find_by_code(code)
        created = user is None
        if user is None:
            first, last = split_name(payload.get("name"))
            representation: dict[str, Any] = {
                "username": code.lower(),
                "enabled": True,
                "attributes": {EMPLOYEE_CODE_ATTRIBUTE: [code]},
                # no credential is ever set: the joiner sets the first password
                "requiredActions": [FIRST_LOGIN_ACTION],
            }
            if first:
                representation["firstName"] = first
            if last:
                representation["lastName"] = last
            email = str(payload.get("work_email") or "").strip()
            if email:
                representation.update(email=email, emailVerified=False)
            self.client.create_user(representation)
            user = self._find_by_code(code)
            if user is None:
                raise KeycloakError(
                    "verification: the created account is not findable", transient=True
                )
        else:
            self._adopt(user, code)
        user_id = str(user["id"])

        assigned: list[str] = []
        role_code = str(payload.get("primary_role") or "").strip()
        if role_code:
            # 05-04 register: fix.role.keycloak_role == the role code (R-nn), 1:1
            role = self.client.get_realm_role(role_code)
            if role is None:
                raise LifecycleFailure(
                    f"realm role {role_code} (the primary role) does not exist in the realm",
                    reason_code="role_not_in_realm",
                    user_id=user_id,
                )
            self.client.add_realm_roles(user_id, [role])
            assigned.append(role_code)

        after = self.client.get_user(user_id)  # report only what the IdP confirms (GV-009)
        if after is None or after.get("enabled") is not True:
            raise KeycloakError("verification: the account is not enabled", transient=True)
        if code not in ((after.get("attributes") or {}).get(EMPLOYEE_CODE_ATTRIBUTE) or []):
            raise LifecycleFailure(
                "Keycloak did not keep the employee_code attribute - declare it in the realm "
                "user profile",
                reason_code="attribute_not_persisted",
                user_id=user_id,
            )
        held = {
            r.get("name") for r in self.client.role_mappings(user_id).get("realmMappings") or []
        }
        if not set(assigned) <= held:
            raise KeycloakError("verification: the role mapping is missing", transient=True)
        return {
            "user": after,
            "created": created,
            "realm_roles_assigned": assigned,
            "required_actions": sorted(after.get("requiredActions") or []),
        }

    def _adopt(self, user: dict[str, Any], code: str) -> None:
        """Reuse an existing account for this employee code (never a second one)."""
        attribute = (user.get("attributes") or {}).get(EMPLOYEE_CODE_ATTRIBUTE)
        if attribute and code not in attribute:
            raise LifecycleFailure(
                f"username {user.get('username')!r} belongs to employee {attribute[0]}",
                reason_code="username_conflict",
                user_id=str(user["id"]),
            )
        if attribute and user.get("enabled") is not False:
            return  # already this employee's active account: nothing to change
        # Full representation: a partial PUT carrying "attributes" would drop the rest.
        representation = {k: user[k] for k in _USER_FIELDS if k in user}
        representation["attributes"] = {
            **(user.get("attributes") or {}),
            EMPLOYEE_CODE_ATTRIBUTE: [code],
        }
        if user.get("enabled") is False:  # a rehire: re-enable, and a new password first
            representation["enabled"] = True
            representation["requiredActions"] = sorted(
                {*(user.get("requiredActions") or []), FIRST_LOGIN_ACTION}
            )
        self.client.update_user(str(user["id"]), representation)

    # ------------------------------------------------------------------ leaver

    def _deprovision(self, payload: dict[str, Any]) -> dict[str, Any]:
        user = self._resolve(payload)
        user_id = str(user["id"])
        self.client.disable_user(user_id)  # first: no new login from here on
        self.client.logout_user(user_id)
        mappings = self.client.role_mappings(user_id)
        realm_roles = list(mappings.get("realmMappings") or [])
        if realm_roles:
            self.client.remove_realm_roles(user_id, realm_roles)
        client_removed: list[str] = []
        for client_name, client in sorted((mappings.get("clientMappings") or {}).items()):
            roles = list(client.get("mappings") or [])
            if roles:
                self.client.remove_client_roles(user_id, str(client["id"]), roles)
                client_removed += [f"{client_name}:{r.get('name')}" for r in roles]
        # Report only what the IdP confirms (GV-009).
        after = self.client.get_user(user_id)
        if after is None or after.get("enabled") is not False:
            raise KeycloakError("verification: the account is still enabled", transient=True)
        if self.client.user_sessions(user_id):
            raise KeycloakError("verification: sessions survived the logout", transient=True)
        return {
            "user": user,
            "realm_roles_removed": sorted(str(r.get("name")) for r in realm_roles),
            "client_roles_removed": client_removed,
        }

    # ------------------------------------------------------------------ events

    def _now_iso(self) -> str:
        return self._now().astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _metadata(event: dict[str, Any]) -> dict[str, Any]:
        # AS-08: same correlation as the M21 event; the M21 event caused this one.
        return {"correlation_id": event["correlation_id"], "causation_id": event["event_id"]}

    def _emit_provisioned(
        self,
        event: dict[str, Any],
        employee_id: int,
        employee_code: str,
        result: dict[str, Any],
        attempts: int,
    ) -> None:
        self._bus().publish_dual(
            "identity.provisioned",
            "hr.employee",
            employee_id,
            {
                "employee_id": employee_id,
                "employee_code": employee_code,
                "keycloak_user_id": str(result["user"]["id"]),
                "username": str(result["user"].get("username") or ""),
                "created": bool(result["created"]),
                "enabled": True,
                "realm_roles_assigned": list(result["realm_roles_assigned"]),
                "required_actions": list(result["required_actions"]),
                "provisioned_at": self._now_iso(),
                "attempts": attempts,
                "joined_event_id": str(event["event_id"] or ""),
            },
            self._metadata(event),
        )

    def _emit_provision_failed(
        self,
        event: dict[str, Any],
        employee_id: int,
        employee_code: str,
        keycloak_user_id: str | None,
        reason_code: str,
        reason: str,
        attempts: int,
    ) -> None:
        self._bus().publish_dual(
            "identity.provision_failed",
            "hr.employee",
            employee_id,
            {
                "employee_id": employee_id,
                "employee_code": employee_code,
                "keycloak_user_id": keycloak_user_id,
                "reason_code": reason_code,
                "reason": reason,
                "failed_at": self._now_iso(),
                "attempts": attempts,
                "joined_event_id": str(event["event_id"] or ""),
            },
            self._metadata(event),
        )

    def _emit_deprovisioned(
        self,
        event: dict[str, Any],
        employee_id: int,
        employee_code: str,
        result: dict[str, Any],
        attempts: int,
    ) -> None:
        self._bus().publish_dual(
            "identity.deprovisioned",
            "hr.employee",
            employee_id,
            {
                "employee_id": employee_id,
                "employee_code": employee_code,
                "keycloak_user_id": str(result["user"]["id"]),
                "username": str(result["user"].get("username") or ""),
                "deprovisioned_at": self._now_iso(),
                "enabled": False,
                "sessions_revoked": True,
                "realm_roles_removed": list(result["realm_roles_removed"]),
                "client_roles_removed": list(result["client_roles_removed"]),
                "attempts": attempts,
                "left_event_id": str(event["event_id"] or ""),
            },
            self._metadata(event),
        )

    def _emit_deprovision_failed(
        self,
        event: dict[str, Any],
        employee_id: int,
        employee_code: str,
        keycloak_user_id: str | None,
        reason_code: str,
        reason: str,
        attempts: int,
    ) -> None:
        self._bus().publish_dual(
            "identity.deprovision_failed",
            "hr.employee",
            employee_id,
            {
                "employee_id": employee_id,
                "employee_code": employee_code,
                "keycloak_user_id": keycloak_user_id,
                "reason_code": reason_code,
                "reason": reason,
                "failed_at": self._now_iso(),
                "attempts": attempts,
                "left_event_id": str(event["event_id"] or ""),
            },
            self._metadata(event),
        )


def outcome_dict(outcome: Outcome) -> dict[str, Any]:
    return asdict(outcome)
