# `IN-003_artefacts/` — Event Registry Artefacts

**Governed by** [`../IN-003_Domain_Event_Catalogue_and_Schema_Registry.md`](../IN-003_Domain_Event_Catalogue_and_Schema_Registry.md)
· **Issued** 2026-08-18 · **CONFIDENTIAL — Internal Use Only**

---

## Contents

```
reconciliation/
  portal-consumed-unpublished.csv    69 rows — the measured consumer-side gap   (IN-003 §7)

schemas/
  service_order.delivered.v1.json    JSON Schema 2020-12 payload exemplar       (IN-003 §4)
  warranty_claim.evidence_incomplete.v1.json   The unpublished CONTROL           (IN-003 §7.4)

service-delivery/
  asyncapi.yaml                      AsyncAPI 3.0 channel contract exemplar     (IN-003 §5)
```

## `reconciliation/portal-consumed-unpublished.csv`

**The measurement this category contributes.** Every event name appearing in a portal's `§12.3`
table that **no module's `§12.3` table declares as published**, extracted at
**2026-08-18 17:40 (+06)** across all twelve portal specifications and all sixty-seven modules.

| Column | Meaning |
|---|---|
| `event_type` | The name the portal consumes |
| `consuming_portals` | Which of P01–P12 depend on it |
| `consumer_count` | How many — `payment.received` is 4, plus the CON-03 contract |
| `triage_class` | `D1` rename · `D2` projection · `D3` genuinely absent · `UNADJUDICATED` |
| `confidence` | `verified` · `heuristic` · `shape` · `no candidate` · `cross-namespace candidate` |
| `published_candidate` | What the producer may already publish under another name |
| `proposed_owning_module` | Who would have to publish it |

**Counted from the file:**

| Class | Rows |
|---|---:|
| `D1` rename | 12 |
| `D2` projection | 7 |
| `D3` genuinely absent | 25 |
| `UNADJUDICATED` | 25 |
| **Total** | **69** |

> **This file is the `RE-04` worklist.** Thirty-six rows are settled; **twenty-five are a judgement
> nobody has yet made.** `IN-003` §7.3.1 states why no tidier split is asserted: the automated triage
> demonstrably under-detects renames, and five were found by hand that it missed.

### How it was produced

```bash
# Published, from every module §12.3                                  → 988
for f in $(find 03_Modules -name 'M[0-9]*.md'); do
  awk 'BEGIN{p=0} /^### 12\.3/{p=1;next} /^### 12\.4/{p=0} /^## /{p=0} p' "$f" \
    | grep -oE '^\| `[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*`' | sed 's/^| //;s/`//g'
done | sort -u > ev_pub.txt

# Consumed, from every portal §12.3, with attribution                 → 102
for f in 03_Modules/K_Platform_and_Technology/P*.md; do
  awk 'BEGIN{x=0} /^### 12\.3/{x=1;next} /^### 12\.4/{x=0} x' "$f" \
    | grep -oE '`[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*`' | sed 's/`//g'
done | sort -u > ev_portal.txt

comm -23 ev_portal.txt ev_pub.txt        # → the 69 rows in this CSV
```

## `schemas/`

JSON Schema 2020-12 payload exemplars. **Two, deliberately chosen:**

| File | Why this event |
|---|---|
| `service_order.delivered.v1.json` | The base case, and the estate's highest-consequence business event — it is the **billable event** M20 consumes |
| `warranty_claim.evidence_incomplete.v1.json` | **`AUDIT-016` `AP-01`'s suppression control.** It is a control, not a convenience, and **no module publishes it.** The schema is issued so the gap is a missing *emitter*, not a missing *design* |

Per `IN-003-D-01` these become **generator fixtures**: the registry's schema emitter is correct when
it reproduces them.

## `service-delivery/asyncapi.yaml`

One of the eleven documents `IN-003` §5.1 requires, generated per bounded context. Demonstrates the
three channels (`domain`, `external`, `platform`), the envelope as a reusable `messageTrait`, the
partition-key binding, and per-operation `send`/`receive` declarations.

## Validation

```bash
python -c "import yaml,glob;[yaml.safe_load(open(f,encoding='utf-8')) for f in glob.glob('**/*.yaml',recursive=True)]"
python -c "import json,glob;[json.load(open(f,encoding='utf-8')) for f in glob.glob('schemas/*.json')]"
npx @asyncapi/cli validate service-delivery/asyncapi.yaml
```

## Status

| Property | Position |
|---|---|
| **Naming** | Every `event_type` here uses **convention A** (`<aggregate>.<past_tense_verb>`, ADR-017). **ADR-017 is unratified** — `IN-003` Q-01 |
| **Renames pending** | **242 of the 988 declared events use a convention-B module-code namespace** and are scheduled for rename in W1 while it is still a text edit (`RE-03`) |
| **Coverage** | 2 schemas of 988. The remainder are scheduled in `IN-003` §11.2 |

---

*`IN-003_artefacts` · Category 04 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
