#!/usr/bin/env python3
"""drill_build_once_promote.py — Gate GP-12 Build-Once-Promote & Rollback Drill record.

Discharges GP-12 (D14) only when every element is measured:
1. Build-once: a single immutable container artifact digest built at CI.
2. Promote: the same digest promoted unchanged across dev -> sit -> uat -> staging.
3. Probing: /healthz probes against each environment during rollout.
4. Rollback rehearsal: an injected canary anomaly triggers automated rollback to the
   prior verified digest with health restored.

GV-009: the previous version hashed a string to make a "digest", reported 10/10
probes, an HTTP 200, a 1250 ms canary spike and a 4.2 s rollback without sending a
request or touching a deployment. Now:
  GP12_PROBE_<ENV>   N GETs against the URL in env var GP12_HEALTHZ_URL_<ENV>;
                     PASS only if every probe returns HTTP 200, UNMEASURED if no URL
  GP12_DIGEST_<ENV>  deployed image digest per environment - needs registry/cluster
                     access, never available to this tool -> UNMEASURED
  GP12_ROLLBACK      canary fault + automated rollback - this tool never injects
                     faults or changes deployments -> UNMEASURED

Emits docs/traceability/evidence/r10-m04-gp12-drill-evidence.json
Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE (a check is UNMEASURED).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
EVIDENCE_NAME = "r10-m04-gp12-drill-evidence.json"

PASS = "PASS"  # noqa: S105 - a verdict label, not a credential
FAIL = "FAIL"
UNMEASURED = "UNMEASURED"
INCOMPLETE = "INCOMPLETE"

RELEASE_TAG = "v2.0.0-rc.1"
ENVIRONMENTS = ("dev", "sit", "uat", "staging")
PROBES_PER_ENVIRONMENT = 10
PROBE_TIMEOUT_SECONDS = 5


def make_check(check_id: str, status: str, detail: str, **measured: object) -> dict:
    return {"id": check_id, "status": status, "detail": detail, **measured}


def overall_verdict(checks: list[dict]) -> str:
    statuses = {check["status"] for check in checks}
    if not statuses:
        return UNMEASURED
    if FAIL in statuses:
        return FAIL
    return PASS if statuses == {PASS} else INCOMPLETE


def exit_code(verdict: str) -> int:
    return {PASS: 0, FAIL: 1}.get(verdict, 2)


def http_status(url: str) -> int | None:
    """HTTP status of one GET, or None when the endpoint did not answer."""
    try:
        with urllib.request.urlopen(url, timeout=PROBE_TIMEOUT_SECONDS) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, OSError, ValueError):
        return None


def probe_environment(env: str, environ: dict | None = None) -> dict:
    environ = os.environ if environ is None else environ
    check_id = f"GP12_PROBE_{env.upper()}"
    url = environ.get(f"GP12_HEALTHZ_URL_{env.upper()}")
    if not url:
        return make_check(
            check_id,
            UNMEASURED,
            f"no health endpoint configured (set GP12_HEALTHZ_URL_{env.upper()})",
            environment=env,
            probe_endpoint=None,
            probes_sent=0,
            probes_passed=0,
        )
    statuses = [http_status(url) for _ in range(PROBES_PER_ENVIRONMENT)]
    passed = sum(1 for s in statuses if s == 200)
    answered = [s for s in statuses if s is not None]
    measured = {
        "environment": env,
        "probe_endpoint": url,
        "probes_sent": len(statuses),
        "probes_passed": passed,
        "http_statuses": sorted(set(answered)),
    }
    if not answered:
        return make_check(check_id, UNMEASURED, f"{url} did not answer", **measured)
    status = PASS if passed == len(statuses) else FAIL
    return make_check(check_id, status, f"{passed}/{len(statuses)} probes HTTP 200", **measured)


def run_build_once_promote_drill(
    evidence_dir: Path = EVIDENCE_DIR, environ: dict | None = None
) -> dict:
    probes = [probe_environment(env, environ) for env in ENVIRONMENTS]
    digests = [
        make_check(
            f"GP12_DIGEST_{env.upper()}",
            UNMEASURED,
            "the deployed image digest needs registry/cluster access, not available to this tool",
            environment=env,
            deployed_digest=None,
        )
        for env in ENVIRONMENTS
    ]
    rollback = make_check(
        "GP12_ROLLBACK",
        UNMEASURED,
        "canary fault injection and automated rollback need a live staging cluster; "
        "this tool never injects faults or changes deployments",
        rollback_duration_seconds=None,
    )
    checks = [*digests, *probes, rollback]
    verdict = overall_verdict(checks)
    evidence = {
        "drill": "GP-12: Build-Once-Promote & Rollback Rehearsal",
        "task": "R10-M04-T04",
        "tool": "tooling/scripts/drill_build_once_promote.py",
        "timestamp": datetime.now(UTC).isoformat(),
        "release_tag": RELEASE_TAG,
        "immutable_digest": None,
        "summary": {
            s.lower(): sum(1 for c in checks if c["status"] == s) for s in (PASS, FAIL, UNMEASURED)
        },
        "promotion_ladder": probes,
        "digest_checks": digests,
        "rollback_rehearsal": rollback,
        "status": verdict,
        "gp_12_discharged": verdict == PASS,
    }
    evidence_dir.mkdir(parents=True, exist_ok=True)
    out_file = evidence_dir / EVIDENCE_NAME
    out_file.write_bytes((json.dumps(evidence, indent=2) + "\n").encode("utf-8"))
    return evidence


def main() -> int:
    print("=" * 80)
    print("1000FiX — Gate GP-12 Build-Once-Promote & Rollback Drill (R10-M04-T04)")
    print("=" * 80)
    drill = run_build_once_promote_drill()
    for check in [*drill["digest_checks"], *drill["promotion_ladder"], drill["rollback_rehearsal"]]:
        print(f"[{check['status']}] {check['id']}: {check['detail']}")
    print("-" * 80)
    print(f"Drill outcome: {drill['status']} | GP-12 discharged: {drill['gp_12_discharged']}")
    print(f"Evidence written to: docs/traceability/evidence/{EVIDENCE_NAME}")
    return exit_code(drill["status"])


if __name__ == "__main__":
    sys.exit(main())
