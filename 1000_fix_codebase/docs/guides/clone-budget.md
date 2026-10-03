# Clone-time and repository-size budget (P02-M04-T10)

**Measured expectation (`BE-004` §11): the clone — Odoo submodule + 20 OCA
subtrees — takes 20–40 minutes.** It is the largest single item in the
onboarding budget (`DE-21`), and it is measured per joiner, not assumed.

## What makes it big

| Component | Approx. history size | Notes |
|---|---|---|
| Odoo (`vendor/odoo`) | ~1.5–2 GB full history | Annual-version history back to 4.2 |
| 20 OCA subtrees (squashed) | ~200–600 MB | `git subtree add --squash` keeps one merge commit each |
| First-party tree | small | This repository's own content |

## Accelerator: partial clone (requires git ≥ 2.40 — hence the floor)

```bash
git clone --filter=blob:none <repo-url> 1000fix-erp
cd 1000fix-erp
git submodule update --init --filter=blob:none vendor/odoo
```

Blobs download lazily on checkout; the wall-clock saving on the Odoo submodule
is the difference between the 20-minute and the 40-minute end of the budget.
**Trade-off recorded:** lazy blobs mean occasional on-demand fetches later;
acceptable on developer machines, NOT in CI (CI clones full for reproducibility
and caches the vendor directory).

## Budget acceptance rule

If a joiner's clone exceeds **40 minutes** on a RECOMMENDED-class machine,
that is a defect against `BE-004` §11 — record it with the joiner's
onboarding-SLA form (`docs/guides/onboarding-sla.md`). Options in order:
partial clone by default → subtree re-squash (drops per-subtree history) →
git-lfs for binary-heavy paths. Each option is a change to `BE-004` under
change control, never a local workaround.
