## What and why

<!-- One paragraph: what this PR does and why. Link the requirement (FR-/NFR- id) and the CD item. -->

**CD item:** `CD-<UNIT>-<nn>`   **Requirement/rule:** `<FR-…/NFR-…/AS-…/DE-…>`

## How verified

<!-- Evidence, not assertion: commands run, screenshots, test output. "Tested" alone is not evidence. -->

- [ ] Unit tests (>=80%; 100% if financial/tax path — DoD-03)
- [ ] Manual verification steps (list them)

## Risk class

<!-- P0-path / financial / statutory (Mushak, payroll) / residency-touching / none-of-these -->

- [ ] This change touches a **residency-classified field path** (if yes: `FF-09` review + `libs/py/fix_residency` only)
- [ ] This change touches **`vendor/`** (if yes: stop — requires a `FORKS.yaml` entry with Design Authority approval)

## Screenshots / output

<!-- UI changes: before/after, Bengali AND English renderings (DE-17). Others: command output. -->

## Checklist

- [ ] Commit convention `<type>(CD-…): <subject>` followed
- [ ] `pre-commit run -a` green locally
- [ ] No new warnings introduced (`--max-warnings=0`)
- [ ] Translations complete at 100% for any user-facing string (DoD-08)
- [ ] Review-only rules considered where relevant: `PYS-22` sudo justification · `PYS-20` timeout/retry/fallback · `FL-03` single offline engine · `SQL-05` two-release column lifecycle
