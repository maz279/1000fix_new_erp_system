#!/usr/bin/env python3
"""validate-workflow - R01-M03 structural check of the GitHub Actions pipeline.

No local tool can prove a workflow *passes*; only a real runner can. But a
workflow that cannot even *start* (wrong location, jobs that never check out
the code, `uv run` with no uv, branch protection requiring jobs that do not
exist) is detectable statically - and the 2026-10 history shows exactly that
class of defect went unnoticed because nothing checked it.

Checks:
  W1  workflow lives at <git-root>/.github/workflows/ (GitHub reads nowhere else)
  W2  defaults.run.working-directory points at this codebase directory
  W3  every job with a `run:` step checks out the repository first
  W4  every job that calls `uv` sets up uv; every job calling npm/npx/node sets up node
  W5  every repo-local script a step invokes exists on disk
  W6  required status-check contexts in .github/settings.yml are real job ids
  W7  CODEOWNERS at a location GitHub honours, patterns without literal quotes
  W8  known-invalid commands absent (gitleaks --redexit, `artifacts upload`)
  W9  every install of vendor/odoo/requirements.txt applies the security
      overrides (tooling/ci/odoo-security-overrides.txt, which must exist), and
      every job running pip-audit installs that Odoo runtime set first - an
      audit of the uv lock alone never sees Odoo's pins (R01 re-audit)
Exit 0 all pass - 1 any failure. Usage: python tooling/ci/validate-workflow.py
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import yaml

CODE = pathlib.Path(__file__).resolve().parents[2]
ODOO_REQS = "vendor/odoo/requirements.txt"
ODOO_OVERRIDES = "tooling/ci/odoo-security-overrides.txt"


def git_root() -> pathlib.Path:
    out = subprocess.run(
        ["git", "-C", str(CODE), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return pathlib.Path(out).resolve()


def main() -> int:
    root = git_root()
    prefix = CODE.relative_to(root).as_posix() if root != CODE else "."
    failures: list[str] = []
    ok = lambda cond, msg: None if cond else failures.append(msg)  # noqa: E731

    wf_path = root / ".github" / "workflows" / "ci.yml"
    ok(
        wf_path.is_file(),
        f"W1 workflow missing at {wf_path} (GitHub reads only <git-root>/.github/workflows)",
    )
    stray = CODE / ".github" / "workflows"
    ok(root == CODE or not any(stray.glob("*.y*ml")), f"W1 stray workflows under {stray} never run")
    if not wf_path.is_file():
        return report(failures)

    wf = yaml.safe_load(wf_path.read_text(encoding="utf-8"))
    wd = ((wf.get("defaults") or {}).get("run") or {}).get("working-directory")
    ok(
        prefix == "." or wd == prefix,
        f"W2 defaults.run.working-directory is {wd!r}, expected {prefix!r}",
    )

    jobs: dict = wf.get("jobs") or {}
    for jid, job in jobs.items():
        steps = job.get("steps") or []
        uses = [s.get("uses", "") for s in steps]
        runs = [(s.get("run") or "") for s in steps]
        if any(runs):
            first_run = next(i for i, s in enumerate(steps) if s.get("run"))
            ok(
                any(u.startswith("actions/checkout") for u in uses[:first_run]),
                f"W3 job '{jid}' runs commands without actions/checkout first",
            )
        text = "\n".join(runs)
        if re.search(r"\buv\b", text):
            ok(
                any(u.startswith("astral-sh/setup-uv") for u in uses),
                f"W4 job '{jid}' calls uv without astral-sh/setup-uv",
            )
        if re.search(r"\b(npm|npx|node)\b", text):
            ok(
                any(u.startswith("actions/setup-node") for u in uses),
                f"W4 job '{jid}' calls node/npm without actions/setup-node",
            )
        for s in steps:
            run = s.get("run") or ""
            base = CODE
            if s.get("working-directory"):
                base = root / s["working-directory"]
            for m in re.finditer(
                r"(?:python|bash|node)\s+((?:tooling|services|libs|i18n|contracts)/[\w./-]+\.(?:py|sh|mjs|js))",
                run,
            ):
                ok(
                    (base / m.group(1)).is_file(),
                    f"W5 job '{jid}' invokes missing script {m.group(1)}",
                )
            ok("--redexit" not in run, f"W8 job '{jid}': gitleaks has no --redexit flag")
            ok(
                "artifacts upload" not in run,
                f"W8 job '{jid}': `artifacts upload` is not a command",
            )
        odoo_installs = [
            i
            for i, s in enumerate(steps)
            if ODOO_REQS in (s.get("run") or "") and "pip install" in (s.get("run") or "")
        ]
        for i in odoo_installs:
            ok(
                f"--override {ODOO_OVERRIDES}" in steps[i]["run"],
                f"W9 job '{jid}' installs {ODOO_REQS} without --override {ODOO_OVERRIDES}",
            )
        for i, s in enumerate(steps):
            if re.search(r"\bpip-audit\b", s.get("run") or ""):
                ok(
                    any(j < i for j in odoo_installs),
                    f"W9 job '{jid}' runs pip-audit before/without installing {ODOO_REQS}",
                )
    ok((CODE / ODOO_OVERRIDES).is_file(), f"W9 {ODOO_OVERRIDES} missing")

    settings = root / ".github" / "settings.yml"
    if settings.is_file():
        cfg = yaml.safe_load(settings.read_text(encoding="utf-8")) or {}
        for br in cfg.get("branches") or []:
            ctx = (
                ((br.get("protection") or {}).get("required_status_checks") or {}).get("contexts")
            ) or []
            for c in ctx:
                ok(
                    c in jobs,
                    f"W6 branch '{br.get('name')}' requires status check '{c}' - no such job",
                )
    else:
        failures.append("W6 .github/settings.yml missing at the repository root")
    stray_settings = CODE / ".github" / "settings.yml"
    ok(
        root == CODE or not stray_settings.exists(),
        f"W6 stray {stray_settings} is ignored by Probot",
    )

    owners = [
        p
        for p in (
            root / ".github" / "CODEOWNERS",
            root / "CODEOWNERS",
            root / "docs" / "CODEOWNERS",
        )
        if p.is_file()
    ]
    ok(bool(owners), "W7 no CODEOWNERS at <git-root>, .github/ or docs/")
    for p in owners:
        bad = [
            ln
            for ln in p.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#") and '"' in ln.split()[0]
        ]
        ok(not bad, f"W7 {p.name}: {len(bad)} pattern(s) contain literal quotes (match nothing)")
    ok(
        root == CODE or not (CODE / "CODEOWNERS").exists(),
        "W7 stray codebase-level CODEOWNERS is ignored by GitHub",
    )

    print(f"validate-workflow: {len(jobs)} jobs checked in {wf_path.relative_to(root).as_posix()}")
    return report(failures)


def report(failures: list[str]) -> int:
    for f in failures:
        print(f"FAIL {f}")
    print("validate-workflow:", "PASS" if not failures else f"{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
