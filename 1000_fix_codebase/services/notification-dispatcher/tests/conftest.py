"""Shared fixtures for the notification-dispatcher suite.

Every channel adapter reads its gateway URL/token from the environment when it
is constructed. Clearing those variables for every test keeps each adapter in
its dry-run default (and FIX_ENV at its local default) unless a test
configures one explicitly through ``monkeypatch`` — so no test can reach a
real gateway and no test leaks configuration into another suite.
"""

from __future__ import annotations

import pytest

DISPATCHER_ENV_VARS = (
    "FIX_ENV",
    "FIX_ACTIVE_WAVE",
    "FIX_NOTIFICATION_DISPATCHER_PORT",
    "FIX_SMS_GATEWAY_URL",
    "FIX_SMS_GATEWAY_TOKEN",
    "FIX_SMS_REDUNDANT_GATEWAY_URL",
    "FIX_SMS_REDUNDANT_GATEWAY_TOKEN",
    "FIX_SMS_REDUNDANT_ONLY",
    "FIX_WHATSAPP_API_URL",
    "FIX_WHATSAPP_API_TOKEN",
    "FIX_EMAIL_API_URL",
    "FIX_EMAIL_API_TOKEN",
    "FIX_NOVU_API_URL",
    "FIX_NOVU_API_TOKEN",
    "FIX_INAPP_API_URL",
    "FIX_INAPP_API_TOKEN",
    "FIX_ALERT_WEBHOOK_URL",
    "FIX_ALERT_WEBHOOK_TOKEN",
)


@pytest.fixture(autouse=True)
def _isolated_dispatcher_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in DISPATCHER_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
