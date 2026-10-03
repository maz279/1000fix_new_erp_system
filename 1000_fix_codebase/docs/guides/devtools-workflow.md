# DevTools workflow — browser preview, performance budget, accessibility (P02-M07)

## 1. Browser preview — all loopback (`EP-12`/`DE-04`)

| Surface | URL | Notes |
|---|---|---|
| Next.js dev server | `http://127.0.0.1:3000` | Turbopack HMR (`D-026`: 16.3 line) |
| Odoo | `http://127.0.0.1:8069` | `dev=all`; XML/Python reload without restart |
| Storybook (`libs/ts/ui`) | `http://127.0.0.1:6006` | Optional; the **only** Vite in the programme — a devDependency that ships nothing |
| Mailpit | `http://127.0.0.1:8025` | The only mail sink (`DE-07`) |

Everything binds `127.0.0.1`, never `0.0.0.0`. Verify in one line:

```powershell
Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in 3000,6006,8069,8025 -and $_.LocalAddress -ne '127.0.0.1' }
# no output = loopback clean
```

## 2. Performance budget — Lighthouse, before CI does (`NFR` bundle, stage 11)

**Portal `P01`'s booking path must be under 400 KB on 3G.** CI gates this
(pre-merge stage 11); check locally first so CI is never the first place you
see it:

1. DevTools → Lighthouse → **Performance + Mobile**, throttling preset
   **Slow 3G** (or set Network throttling manually: 400 kb/s, 400 ms RTT).
2. Record on the booking path (`/` → service select → slot → confirm).
3. Read the **transferred** bytes in Network (not "size": gzip is what 3G
   pays for). Budget: **< 400 KB** across the path.
4. Regression: compare against the last merge — a +20 KB jump needs a
   sentence in the PR, not just a pass.

## 3. Accessibility — axe DevTools, the automated *minority* (`UX-005`/`QA-008`)

Install the axe DevTools extension; run a scan on every new screen at both
breakpoints. **Automated scans find a minority of WCAG 2.2 AA failures** —
the manual half (keyboard trap, focus order, meaningful labels in Bengali
renderings) is resourced by `QA-008` §6 and is a review item, not a tool
output. CI stage 12 runs axe-core on builds; zero-violation policy.

## 4. Application panel — PWA offline shell (`URD` §20)

Customer portal `P01` ships an offline shell: verify in Application →
Service Workers + Manifest that the shell precache loads with the network
offline, in **both Chrome and Firefox** (Bengali conjunct shaping differs
between engines — the same page must be checked in both).

## 5. Debugging Odoo (Windows-native, `D-WS-001`)

The `.vscode/launch.json` configurations are the canonical Linux shapes. On
the Windows baseline Odoo runs **containerised**:

- **Hot reload (doctor check 14):** the compose dev service mounts
  `addons/` and runs `odoo-bin -c /etc/odoo/local.conf --dev=all` — Python
  and XML edits apply without restart; manifest/model/field edits need
  `make upgrade MODULE=cd_x` + restart.
- **Breakpoints (doctor check 13):** attach VS Code Python → Remote Attach to
  the container's debugpy port (5678, loopback-published); set the breakpoint
  in the `cd_` model and drive the request from the browser. Containerised
  debugging is the recorded consequence #1 of `D-WS-001`; checks 13/14 were
  re-scoped to their container equivalents, not dropped.

## 6. Flutter DevTools (`D-027`; `TAF-58` device-lab honesty)

`fvm flutter pub global run devtools` against the running app. At least one
**Android emulator profile** is configured (emulator coverage pre-merge);
**real-device coverage is gate-only** because the device lab is unfunded
(`Q-04`) — **the reduction is declared, not silent**.
