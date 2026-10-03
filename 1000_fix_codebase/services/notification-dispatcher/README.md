# notification-dispatcher — P04-M05 (M27 / CD-M27-nn)

> **One event, one decision.** Every module publishes an event; exactly one
> component decides how it is delivered. This service is that component
> (`AR-009` / `AS-08` / `NT-001`).

## What it does

Domain modules write events to `cd_event_outbox` in the same transaction as
the business write. `libs/py/fix_events` (FF-28 — the only event client)
hands them to `Dispatcher.handle()`. The dispatcher then:

1. **Routes** — the NT-001 event-channel matrix decides audience, channels,
   templates and consent class. A domain module never chooses a channel.
2. **Suppresses** — NT-002 consent preferences, BTRC DND, NT-003 send windows
   (Asia/Dhaka), rolling frequency caps and QH-03 staleness discard.
3. **Delivers** — channel adapters for INT-010 SMS (masking/non-masking per
   BD-01/BD-02), INT-012 WhatsApp, INT-013 email (Mailpit in non-production,
   EP-11), Novu push, NT-018 in-app and NT-021 alerts.
4. **Tracks** — every attempt recorded; SMS/push/email retry exactly once,
   then the NT-001 §4 fallback ladder; all-channels-failed raises an
   operational task — **never a silent drop**.
5. **Measures** — delivery rate, p50/p95 latency, channel mix, opt-out rate
   (DoD-09), exposed for M25 in Phase 7.

## Layout

```
services/notification-dispatcher/
├── Dockerfile              DE-06 digest placeholder + DE-11 env guard
├── templates/
│   └── nt-registry.json    the 26 NT-* files as a machine-readable registry
│                           (W1 lifecycle bodies in Bengali and English)
├── src/
│   ├── policy.py           NT-002 consent classes + NT-003 QH-01…QH-04, caps
│   ├── router.py           NT-001 matrix + CH-01…CH-06 channel rules
│   ├── channels.py         INT-010/012/013 adapters — SSRF-guarded, dry-run default
│   ├── delivery.py         tracking, retry-once, fallback ladder, DLQ, IP-09 register
│   ├── kpis.py             the four KPI families (OTP excluded per NT-007)
│   ├── dispatcher.py       the decision engine
│   └── main.py             /health /kpis /dlq /fallbacks + consume entry
└── tests/                  37 tests — every numbered rule gets one
```

## Safety properties (all test-enforced)

| Property | Rule |
|---|---|
| Dry-run by default | No gateway env var ⇒ decided, logged, counted — no packet leaves |
| Credentials | Environment variables only; URL-embedded or query-string credentials refused |
| SSRF | Non-production hosts jailed to loopback/compose names; production must be https |
| BD-02/BD-03 | Marketing never uses the masking route; promotional copy never carries the masking signature |
| CH-06 | The on-call `alert` channel is internal-only |
| QH-01/02 | Security/transactional send 24/7; service/marketing are held, never dropped |
| QH-03 | A held message stale at window-open is discarded |
| NT-001 §4 | Retry once, then fallback ladder; total failure raises a task |
| OTP privacy | OTP events excluded from KPIs; content never enters tracking records |

## Run

```powershell
# tests (stdlib only — nothing to install)
py -3.12 -m unittest discover -s services/notification-dispatcher/tests -t services/notification-dispatcher

# in compose (integration profile; email routes to Mailpit per EP-11)
docker compose --profile core --profile integration up notification-dispatcher
```

## Environment variables (never literals — Mimosa/deployment rule)

| Variable | Purpose |
|---|---|
| `FIX_ENV` | `local`/`staging`/`production` — gates the SSRF allowlist (DE-11 refuses others at startup) |
| `FIX_ACTIVE_WAVE` | W1…W5 — later-wave events are refused, not accidentally delivered |
| `FIX_SMS_GATEWAY_URL` / `_TOKEN` | INT-010 aggregator (BTRC-listed) |
| `FIX_WHATSAPP_API_URL` / `_TOKEN` | INT-012 (DEP-19) |
| `FIX_EMAIL_API_URL` / `_TOKEN` | INT-013 — compose sets this to Mailpit |
| `FIX_NOVU_API_URL` / `_TOKEN` | push gateway (P04-M05-T01) |
| `FIX_ALERT_WEBHOOK_URL` / `_TOKEN` | NT-021 on-call alerting |

## Roadmap crosswalk

| Task | Status |
|---|---|
| T01 Novu deployed | compose `novu` service (integration profile) |
| T02 dispatcher consuming outbox events | this service — `fix_events.consume(handler=dispatcher.handle)` |
| T03 INT-010 SMS (+INT-011 designed) | `SMSChannel`; INT-011 raises not-implemented until W2 |
| T04 INT-012 WhatsApp | `WhatsAppChannel` (dry-run until DEP-19 lands) |
| T05 INT-013 email → Mailpit | `EmailChannel` + compose env (EP-11) |
| T06 routing, preferences, quiet hours | `router.py` + `policy.py` |
| T07 26 NT-* templates bn+en | `templates/nt-registry.json` |
| T08 delivery tracking, retry, DLQ | `delivery.py` |
| T09 P0 fallback register | `delivery.FALLBACK_REGISTER` (IP-09/OP-014) |
| T10 notification KPIs | `kpis.py` + `/kpis` endpoint |
