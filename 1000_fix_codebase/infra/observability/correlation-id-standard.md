# Correlation-ID standard — NFR-092 / PE-008 (P06-M08-T05/T06)

> **A single correlation id across every hop.** Without it, a support ticket
> about "the invoice never came" is an archaeology project; with it, it is
> one query.

## The identifier

| Aspect | Rule |
|---|---|
| Name | `x-fix-correlation-id` (HTTP header), `correlation_id` (event metadata, log field, trace attribute) |
| Format | UUID v4, generated at the ORIGIN of a user interaction (portal controller, dispatcher consumer, cron tick) |
| Propagation | Every service-to-service call forwards it verbatim; the outbox writes it into event metadata; Odoo context keys carry it through the ORM |
| Never | Re-generated mid-chain, derived from user data, or used as a business key |

## Injection points (this phase's surface)

1. **Odoo Web / API** — a `ir.http` dispatch hook reads the header into
   `env.context["fix_correlation_id"]`; every `fix_events.publish` stamps it
   into the outbox row's metadata.
2. **Services** (notification-dispatcher, pricing-engine, reconciliation,
   payment-connectors, document-generation) — read the header; return it in
   responses; include it in every structured log line and OTel span
   attribute (`fix.correlation_id`).
3. **OpenTelemetry** — W3C `traceparent` carries hop-level tracing; the
   correlation id is the LONGER-lived business identifier and rides as a
   span attribute + baggage entry so it survives async hops through the
   outbox where a trace context would break.
4. **Logs** — Loki structured-log field on every line: `{"correlation_id": "..."}`.

## Query path (the point)

`{correlation_id="uuid"}` in Loki returns every log line; the same value in
Tempo's search returns every span; the outbox table's metadata JSON indexes
it for event replay. One id, three systems, one answer.

## Verification

FF-33 (performance, this phase's activation) exercises 1.5x-peak traffic
through the full chain; its success criteria include "a sampled
correlation id appears in >= 99% of hop logs for its interaction".
