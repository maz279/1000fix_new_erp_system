# Odoo layer runbook (layers 3–2)

## Process facts (this machine)

- Odoo runs on the HOST, not docker:
  `python vendor/odoo/odoo-bin -c infra/odoo-conf/local.resolved.conf -d fix_dev --dev=all`
- **PYTHONPATH must include the repo root** or `libs.py.*` imports fail at
  boot (every page 500s). Restart pattern:
  ```bash
  cd 1000_fix_codebase
  PYTHONPATH="$(pwd)" python vendor/odoo/odoo-bin -c infra/odoo-conf/local.resolved.conf -d fix_dev --dev=all
  ```
- DB `fix_dev` on compose-postgres-1 (127.0.0.1:5433, user fix).
- Admin RPC login: `admin` / `admin` (db fix_dev) — never the
  `change-me-dev-only` values (those are DB-manager/env passwords).

## Hot-reload truth table

| Change | Hot-reloads under --dev=all? |
|---|---|
| Model .py edit (existing module) | usually yes |
| **New controller file / controllers dir** | **NO — process restart** |
| New module install | via RPC `ir.module.module` (update_list → button_immediate_install) |
| View XML | needs `-u module` or button_immediate_upgrade |
| kong/qweb templates | qweb mode yes |

After `button_immediate_install/upgrade`: sessions die ("Session expired"
on next RPC) — re-login in your probe client.

## Installing/upgrading modules via RPC (no CLI restart)

```python
c.call("ir.module.module", "update_list", [])
ids = c.call("ir.module.module", "search", [[["name","=","cd_customer_portal"]]])
c.call("ir.module.module", "button_immediate_install", [ids])   # or _upgrade
```
Wrap calls with re-login on "Session expired" (registry reloads kill sessions).

## Logging

- Pseudo-levels: `--log-level=debug_sql` (all SQL), `debug_rpc`,
  `debug_rpc_answer`; targeted: `--log-handler=odoo.addons.cd_:DEBUG`
  (already in local.resolved.conf).
- The werkzeug ACCESS LOG lines (`"POST /path HTTP/1.1" 200 - …`) are the
  single most under-used forensic tool on this estate: they show the EXACT
  path Odoo received (proved Kong strip_path bug) and response codes.

## Debuggers

- `--dev=pudb` (post-mortem console debugger) — needs an interactive TTY;
  prefer adding `import pdb; pdb.set_trace()` (or `breakpoint()`) at the
  suspected line for local repro, then remove.
- Odoo shell for ORM probes: `odoo-bin shell -d fix_dev` (PYTHONPATH!).

## Controller invariants (each = a locked regression)

1. Dispatcher passes EVERY JSON-RPC param as kwarg → helpers taking a
   positional `brand_id`-style key must `kwargs.pop(key, None)` first.
2. Never put explicit `None` into create() vals for fields with defaults.
3. Combined endpoints (list+create on one path): JSON-RPC routes are always
   POST; two @http.route on the same path conflict — branch INSIDE.
4. `type="json"`, `auth="user"`; readonly=True unless the handler writes.
5. Writes must call model action methods (AS-09); money formatted via
   `_fmt_bdt` helper (AS-10), never client-side.
6. Field names: verify against the model file, not memory
   (`fix.ar.invoice.taxable_amount`, `fix.device.imei_1`,
   `fix.device.device_model_id.name`).

## Live-fire law

Source tests prove shape; only a live RPC proves behavior. After any
controller change: `python tooling/scripts/livefire-pp5.py` (45 checks)
+ battery §5.5 of SKILL.md.
