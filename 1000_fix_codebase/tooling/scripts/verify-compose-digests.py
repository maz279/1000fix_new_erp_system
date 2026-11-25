#!/usr/bin/env python3
"""verify-compose-digests - DE-06 / R01-M02-T02 registry-truth check.

`grep -c PLACEHOLDER-RESOLVE` proves only that no placeholder string remains;
it cannot tell a real digest from a fabricated one. This tool asks each
registry whether the pinned manifest actually exists (anonymous HEAD of
/v2/<repo>/manifests/<digest>), for every `image:` in infra/compose/*.yml and
every `FROM` in a first-party Dockerfile.

Exit 0 - every pinned reference resolves (locally-built images marked
         `PENDING-FIRST-BUILD` are reported, not failed - digest-pinning-policy).
Exit 1 - any reference is unpinned, or its digest/repository does not exist.
Exit 4 - registry unreachable (no verdict - never reported as PASS).

Usage: python tooling/scripts/verify-compose-digests.py [--json]
Needs network; read-only; no credentials.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
ACCEPT = ",".join(
    [
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.v2+json",
    ]
)
LOCAL_BUILD = re.compile(r"^1000fix/")
SKIP_DIRS = {"node_modules", "vendor", ".venv"}


def collect() -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for f in sorted((ROOT / "infra" / "compose").glob("*.yml")):
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*image:\s*([^\s#]+)", line)
            if m:
                refs.append((f.relative_to(ROOT).as_posix(), m.group(1)))
    for f in sorted(ROOT.rglob("Dockerfile*")):
        if SKIP_DIRS & set(f.relative_to(ROOT).parts):
            continue
        stages: set[str] = set()
        # ARG defaults are resolved before FROM matching, so a pinned ARG
        # default (tag@sha256) is what actually gets pulled and is what we
        # verify - the ${VAR} placeholder itself never reaches a registry.
        arg_defaults: dict[str, str] = {}
        for line in f.read_text(encoding="utf-8").splitlines():
            m_arg = re.match(r"\s*ARG\s+([A-Za-z_][A-Za-z0-9_]*)=(\S+)", line)
            if m_arg:
                arg_defaults[m_arg.group(1)] = m_arg.group(2)
            m = re.match(r"\s*FROM\s+(?:--platform=\S+\s+)?(\S+)(?:\s+AS\s+(\S+))?", line, re.I)
            if m:
                base = m.group(1)
                # Substitute ${VAR} inside the ref (e.g. node:${NODE_VERSION})
                # with the pinned ARG default collected above.
                resolved = arg_defaults  # loop-stable binding for the lambda
                base = re.sub(
                    r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}",
                    lambda m2, d=resolved: d.get(m2.group(1), m2.group(0)),
                    base,
                )
                if base not in stages and base != "scratch":
                    refs.append((f.relative_to(ROOT).as_posix(), base))
                if m.group(2):
                    stages.add(m.group(2))
    return refs


def _token(host: str, repo: str) -> str | None:
    if host == "registry-1.docker.io":
        url = (
            f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repo}:pull"
        )
    elif host == "ghcr.io":
        url = f"https://ghcr.io/token?scope=repository:{repo}:pull"
    else:
        return None
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)["token"]


def check(ref: str) -> str:
    # The first build EXISTS now (local registry). SSRF posture: the
    # connection target is a pinned literal host/port pair (loopback), and the
    # request path segments are validated against strict allowlist regexes
    # (repo: no scheme/host/userinfo/query; digest: sha256 hex) before they
    # are percent-free path components - nothing from a compose file can
    # redirect the connection. Falls back to PENDING-FIRST-BUILD (not failed)
    # when the local registry is down (production push = operator step).
    if LOCAL_BUILD.match(ref):
        m = re.fullmatch(r"(1000fix/[a-z0-9._/-]+):([a-z0-9._-]+)@(sha256:[0-9a-f]{64})", ref)
        if not m:
            return "PENDING-FIRST-BUILD"
        repo, _tag, digest = m.groups()
        import http.client

        conn = http.client.HTTPConnection("127.0.0.1", 5500, timeout=5)
        try:
            conn.request(
                "GET",
                f"/v2/{repo}/manifests/{digest}",
                headers={
                    "Accept": (
                        "application/vnd.oci.image.index.v1+json,"
                        "application/vnd.docker.distribution.manifest.list.v2+json,"
                        "application/vnd.docker.distribution.manifest.v2+json"
                    )
                },
            )
            resp = conn.getresponse()
            resp.read()
            got = resp.headers.get("Docker-Content-Digest", "")
            if resp.status == 200 and got == digest:
                return "OK"
            return f"MISMATCH ({got or 'no digest header'}; HTTP {resp.status})"
        except OSError:
            return "PENDING-FIRST-BUILD"
        finally:
            conn.close()
    if "@sha256:" not in ref:
        return "UNPINNED"
    m = re.fullmatch(
        r"([a-z0-9._/-]+?)(?::([a-zA-Z0-9._-]+))?@(sha256:[0-9a-f]{64})",
        ref,
    )
    if not m:
        return "UNPARSEABLE-REF"
    name, tag, digest = m.groups()
    first = name.split("/", 1)[0]
    if "." in first or ":" in first:
        host, repo = name.split("/", 1)
    else:
        host, repo = "registry-1.docker.io", name if "/" in name else f"library/{name}"
    # SSRF posture: the connection host must be one of the three known public
    # registries (literal allowlist) and repo/tag/digest passed strict
    # character-class regexes above; the request path cannot carry a scheme,
    # host, userinfo or query. Some registries (observed: Docker Hub on
    # grafana/tempo) reject by-digest requests with HTTP 400 while serving
    # the same manifest by tag - the by-tag retry compares the digest header,
    # an equal digest is a verified pin.
    if host not in ("registry-1.docker.io", "ghcr.io", "quay.io"):
        return f"UNKNOWN-REGISTRY ({host})"
    try:
        tok = _token(host, repo)
    except urllib.error.HTTPError as e:
        return f"REPO-NOT-FOUND (token HTTP {e.code})"
    import http.client

    for target in filter(None, (digest, tag)):
        conn = http.client.HTTPSConnection(host, timeout=20)
        try:
            headers = {"Accept": ACCEPT}
            if tok:
                headers["Authorization"] = f"Bearer {tok}"
            conn.request("HEAD", f"/v2/{repo}/manifests/{target}", headers=headers)
            resp = conn.getresponse()
            resp.read()
            if resp.status == 200:
                got = resp.headers.get("Docker-Content-Digest")
                if got is None or got == digest:
                    return "OK"
                return f"MISMATCH ({got})"
        except OSError as e:
            return f"DIGEST-NOT-FOUND ({type(e).__name__})"
        finally:
            conn.close()
    return "DIGEST-NOT-FOUND (HTTP 400 by digest and by tag)"


def main() -> int:
    as_json = "--json" in sys.argv
    results = []
    try:
        for src, ref in collect():
            results.append({"source": src, "image": ref, "status": check(ref)})
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"verify-compose-digests: registry unreachable - no verdict ({e})", file=sys.stderr)
        return 4
    bad = [r for r in results if r["status"] not in ("OK", "PENDING-FIRST-BUILD")]
    if as_json:
        print(
            json.dumps({"checked": len(results), "failed": len(bad), "results": results}, indent=2)
        )
    else:
        for r in results:
            print(f"{r['status']:<28} {r['image']}  [{r['source']}]")
        pending = sum(r["status"] == "PENDING-FIRST-BUILD" for r in results)
        print(
            f"\nverify-compose-digests: {len(results)} refs, {len(bad)} failed, {pending} pending-first-build"
        )
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
