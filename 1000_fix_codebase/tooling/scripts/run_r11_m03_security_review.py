#!/usr/bin/env python3
"""run_r11_m03_security_review.py — Final Security Review in Production (R11-M03-T01).

Implements:
1. Post-cutover pentest delta: 24 OWASP/ASVS vectors, each measured in this run
   by a read-only live probe of the local Odoo (127.0.0.1:8069), a repo fitness
   check run via subprocess, a repo pytest target, or a static scan of the
   source / infra specs.
2. Vault secret handling: the EP-06 production-mode refusal of the local
   VaultSecretManager is exercised; production rotation is not observable.
3. Key-material custody transfer to operations (a human, dual-control act).
4. Wazuh SIEM / osquery alerting: the manager's enrolment ports are probed.
5. Emits r11-m03-security-closure-report.json and the Markdown report.

GV-009: a vector is PASS or FAIL only when this run measured it; a probe whose
target is unreachable, or a claim that needs production / a human, is
UNMEASURED with the reason. Finding counts are derived from the FAILed vectors.
Verdict: FAIL if anything failed, INCOMPLETE if anything is UNMEASURED, else
PASS. Exit 0 PASS / 1 FAIL / 2 INCOMPLETE.
"""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tooling" / "scripts"))
from vault_secret_manager import VaultSecretManager

EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
DOCS_DIR = REPO_ROOT / "docs" / "traceability"
FITNESS_DIR = REPO_ROOT / "tooling" / "fitness"
VENDOR_CLEAN_SCRIPT = REPO_ROOT / "tooling" / "scripts" / "check-vendor-clean.sh"

ODOO_URL = os.environ.get("FIX_ODOO_URL", "http://127.0.0.1:8069")
WAZUH_HOST, WAZUH_PORTS = "127.0.0.1", (1514, 1515)  # infra/compose/docker-compose.msp.yml

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"
SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
TRACEBACK_MARKER = "Traceback (most recent call last)"

SCAN_SKIP_PARTS = {
    "node_modules",
    "__pycache__",
    ".venv",
    "dist",
    "build",
    ".next",
    ".dart_tool",
    "vendor",
    "htmlcov",
    "odoo-data",
}
SECRET_SCAN_DIRS = (
    "addons",
    "services",
    "libs",
    "infra",
    "tooling",
    "apps",
    "contracts",
    "db",
    "dags",
)
SECRET_SCAN_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".yml", ".yaml", ".json", ".conf", ".xml", ".toml",
    ".ini", ".sh", ".ps1", ".env", ".pem", ".key", ".dart", ".cfg",
}  # fmt: skip
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"),
    "AWS access key": re.compile(r"(?<![A-Z0-9])AKIA[0-9A-Z]{16}(?![A-Z0-9])"),
    "GitHub token": re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"),
}
CODE_SCAN_DIRS = ("addons", "services", "libs")
SQL_REVIEW_MARKER = re.compile(r"noqa:\s*S608\s*-\s*\S")
DB_CONTAINER_PORTS = {"5432", "6379", "9000", "8123", "9092"}
LOOPBACK_BIND = re.compile(r"^(?:127\.0\.0\.1|localhost|\[::1\]):")
COMPOSE_IMAGE = re.compile(r"^\s*image:\s*['\"]?([^\s'\"#]+)")
DOCKER_FROM = re.compile(r"^\s*FROM\s+(\S+)", re.IGNORECASE)
TLS_CONFIG = re.compile(r"ssl_protocols|TLSv1\.3|tls_min_version|min_tls_version|minVersion", re.I)

# The 24 vectors in scope: (code, name, category, severity if FAILed). The
# severity is the classification a failure carries, not a measurement.
VECTORS = [
    ("A01-01", "Unauthenticated Portal Session Rejection", "A01", "HIGH"),
    ("A01-02", "Cross-Tenant IDOR Defense", "A01", "HIGH"),
    ("A01-03", "Broken Object Level Auth (BOLA) Defense", "A01", "HIGH"),
    ("A01-04", "Multi-Company & OU Isolation (AS-03 / FF-21)", "A01", "HIGH"),
    ("A02-01", "Zero Plaintext Secrets in Source Tree", "A02", "CRITICAL"),
    ("A02-02", "PDPA Sovereign Residency Enforcement (FF-09)", "A02", "HIGH"),
    ("A02-03", "TLS 1.3 / mTLS In-Transit Encryption", "A02", "HIGH"),
    ("A03-01", "SQL Injection Parameter Sanitization", "A03", "CRITICAL"),
    ("A03-02", "Arbitrary Command Execution (shell=True / os.system)", "A03", "CRITICAL"),
    ("A03-03", "Dynamic Code Evaluation (eval/exec)", "A03", "HIGH"),
    ("A04-01", "Seller KYC Verification Gate (M12)", "A04", "HIGH"),
    ("A04-02", "Commercial Monetary Tampering Defense", "A04", "HIGH"),
    ("A04-03", "Dispute SLA 48h Lockout & Escalation", "A04", "MEDIUM"),
    ("A05-01", "Stack Trace Masking on Error Responses", "A05", "MEDIUM"),
    ("A05-02", "ClickHouse Analytical Read-Only Boundary (FF-28)", "A05", "HIGH"),
    ("A05-03", "Production Port Surface Hardening", "A05", "HIGH"),
    ("A06-01", "Zero Unauthorized Forks (AS-05 / FF-03)", "A06", "MEDIUM"),
    ("A06-02", "Supply-Chain Dependency Vulnerability Scan", "A06", "HIGH"),
    ("A07-01", "Anti-CSRF Route Policy (no csrf=False opt-outs)", "A07", "MEDIUM"),
    ("A07-02", "Session Rotation Upon Privilege Elevation", "A07", "MEDIUM"),
    ("A08-01", "Insecure Deserialization (pickle) Defense", "A08", "HIGH"),
    ("A08-02", "Container Image Digest Pinning", "A08", "MEDIUM"),
    ("A09-01", "Transactional Audit Logging (FF-20)", "A09", "MEDIUM"),
    ("A09-02", "Privileged Admin Action Audit Trail", "A09", "MEDIUM"),
]

PYTEST_TARGETS = {
    "A01-02": "addons/domain/d_circular/cd_marketplace/tests/test_tenant_isolation_negative.py",
    "A04-01": "addons/domain/d_circular/cd_marketplace/tests/test_seller_api.py::TestKycGate",
    "A04-02": "addons/domain/d_circular/cd_marketplace/tests/test_seller_api.py::TestActionDelegation::test_price_validation_server_side",
    "A04-03": "addons/domain/d_circular/cd_marketplace/tests/test_dispute_sla.py",
}

CUSTODY_SCOPE = [
    "KEY-HSM-001 Z4 Bangladesh DC HSM master key",
    "KEY-VAULT-SHARD-A split-residency vault shard A (Dhaka production)",
    "KEY-VAULT-SHARD-B split-residency vault shard B (offsite escrow)",
    "CERT-MTLS-ROOT internal service-mesh mTLS root CA & intermediates",
    "CERT-TLS-WILDCARD public *.1000fix.com TLS private key",
]
ROTATION_SCOPE = [
    "database/credentials/production:password",
    "auth/keycloak:admin_password",
    "integrations/bkash:app_secret",
    "integrations/nagad:private_key",
]


def derive_verdict(statuses: list[str]) -> str:
    if not statuses:
        return "INCOMPLETE"
    if FAIL in statuses:
        return FAIL
    if any(s != PASS for s in statuses):
        return "INCOMPLETE"
    return PASS


def exit_code_for(verdict: str) -> int:
    return {PASS: 0, FAIL: 1}.get(verdict, 2)


def _list(items: list[str], limit: int = 5) -> str:
    shown = "; ".join(items[:limit])
    return shown + (f"; ... {len(items) - limit} more" if len(items) > limit else "")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


# ------------------------------------------------------------ measurement I/O --


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def http_request(method: str, path: str, jsonrpc: bool = False, timeout: float = 5) -> dict:
    """One read-only request to the local Odoo, redirects NOT followed."""
    data, headers = None, {}
    if jsonrpc:
        payload = {"jsonrpc": "2.0", "method": "call", "params": {}, "id": 1}
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(ODOO_URL + path, data=data, headers=headers, method=method)
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as resp:
            body = resp.read(200_000).decode("utf-8", errors="replace")
            return {"reachable": True, "status": resp.status, "location": "", "body": body}
    except urllib.error.HTTPError as exc:
        body = exc.read(200_000).decode("utf-8", errors="replace") if exc.fp else ""
        location = exc.headers.get("Location", "") if exc.headers else ""
        return {"reachable": True, "status": exc.code, "location": location, "body": body}
    except (urllib.error.URLError, OSError) as exc:
        return {"reachable": False, "status": None, "location": "", "body": "", "error": str(exc)}


def run_fitness(filename: str, root: Path = REPO_ROOT) -> tuple[str, str]:
    """Run one repo fitness check (fixed argv, no shell); PASS iff exit 0."""
    script = root / "tooling" / "fitness" / filename
    if not script.is_file():
        return FAIL, f"{filename} missing - the control is not in the repo"
    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return UNMEASURED, f"{filename} not runnable: {exc}"
    lines = [ln.strip() for ln in (proc.stdout + proc.stderr).splitlines() if ln.strip()]
    verdict = next((ln for ln in lines if re.search(r"\b(OK|PASS|FAIL)\b", ln)), "")
    return (PASS if proc.returncode == 0 else FAIL), (
        f"{filename} exit {proc.returncode}: {verdict or (lines[-1] if lines else 'no output')}"
    )


def run_pytest(target: str, root: Path = REPO_ROOT, timeout: int = 900) -> tuple[str, str]:
    """Run one pytest target; counts come from the JUnit XML it writes.

    PASS needs >= 1 passed and 0 failed/errored; nothing run is UNMEASURED."""
    with tempfile.TemporaryDirectory() as tmp:
        junit = Path(tmp) / "junit.xml"
        cmd = [sys.executable, "-m", "pytest", target, "-p", "no:cacheprovider", "-W", "ignore"]
        cmd.append(f"--junitxml={junit}")
        try:
            proc = subprocess.run(
                cmd, cwd=str(root), capture_output=True, text=True, timeout=timeout, check=False
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return UNMEASURED, f"pytest not runnable: {exc}"
        counts = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
        if junit.is_file():
            xml_root = ET.parse(junit).getroot()  # noqa: S314 - the JUnit file pytest just wrote
            for suite in [xml_root] if xml_root.tag == "testsuite" else xml_root.iter("testsuite"):
                for key in counts:
                    counts[key] += int(suite.get(key, "0") or 0)
    passed = counts["tests"] - counts["failures"] - counts["errors"] - counts["skipped"]
    detail = (
        f"pytest {target.split('/')[-1]}: {passed} passed, {counts['failures']} failed, "
        f"{counts['errors']} errors, {counts['skipped']} skipped (exit {proc.returncode})"
    )
    if proc.returncode == 0 and passed > 0 and not counts["failures"] and not counts["errors"]:
        return PASS, detail
    if proc.returncode in (0, 5) and not counts["failures"] and not counts["errors"]:
        return UNMEASURED, detail + " - nothing ran"
    return FAIL, detail


def _bash() -> str | None:
    git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
    if sys.platform == "win32" and git_bash.is_file():
        return str(git_bash)
    return shutil.which("bash")


def run_vendor_clean(root: Path = REPO_ROOT) -> tuple[int | None, str]:
    bash, script = _bash(), root / "tooling" / "scripts" / "check-vendor-clean.sh"
    if bash is None or not script.is_file():
        return None, "bash or check-vendor-clean.sh unavailable"
    try:
        proc = subprocess.run(
            [bash, str(script)],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)
    lines = [ln.strip() for ln in (proc.stdout + proc.stderr).splitlines() if ln.strip()]
    return proc.returncode, lines[0] if lines else ""


def tcp_open(host: str, port: int, timeout: float = 2) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


# ----------------------------------------------------------------- scanners --


def _iter_files(root: Path, dirs: tuple[str, ...], exts: set[str]):
    for d in dirs:
        base = root / d
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if (
                p.suffix in exts
                and p.is_file()
                and not (SCAN_SKIP_PARTS & set(p.relative_to(root).parts))
            ):
                yield p


def scan_secrets(root: Path) -> dict[str, Any]:
    hits, scanned = [], 0
    for path in _iter_files(root, SECRET_SCAN_DIRS, SECRET_SCAN_EXTS):
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        hits += [
            f"{_rel(path, root)} ({k})" for k, rx in SECRET_PATTERNS.items() if rx.search(text)
        ]
    return {"files_scanned": scanned, "hits": hits}


def _is_test_file(path: Path) -> bool:
    return "tests" in path.parts or "test" in path.parts or path.name.startswith("test_")


def scan_python_sinks(root: Path) -> dict[str, Any]:
    """AST scan of non-test Python for SQL built by string formatting,
    shell=True / os.system, bare eval/exec and pickle deserialisation.

    A string-built execute() whose statement carries a reviewed
    ``# noqa: S608 - <reason>`` (the repo's SQL-02 review marker) is listed
    under ``sql_reviewed``; only unreviewed ones land in ``sql``."""
    out: dict[str, Any] = {"files_scanned": 0, "execute_calls": 0, "sql": [], "shell": []}
    out.update(sql_reviewed=[], eval=[], pickle=[])
    for path in _iter_files(root, CODE_SCAN_DIRS, {".py"}):
        if _is_test_file(path.relative_to(root)):
            continue
        source = path.read_text(encoding="utf-8", errors="ignore")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        src_lines = source.splitlines()
        out["files_scanned"] += 1
        rel = _rel(path, root)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
            base = (
                func.value.id
                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name)
                else None
            )
            where = f"{rel}:{node.lineno}"
            if isinstance(func, ast.Attribute) and name == "execute" and node.args:
                out["execute_calls"] += 1
                arg = node.args[0]
                if (
                    isinstance(arg, ast.JoinedStr)
                    or (isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod | ast.Add))
                    or (isinstance(arg, ast.Call) and getattr(arg.func, "attr", None) == "format")
                ):
                    span = src_lines[node.lineno - 1 : (node.end_lineno or node.lineno)]
                    reviewed = any(SQL_REVIEW_MARKER.search(ln) for ln in span)
                    out["sql_reviewed" if reviewed else "sql"].append(where)
            shell_kw = any(
                k.arg == "shell" and isinstance(k.value, ast.Constant) and k.value.value is True
                for k in node.keywords
            )
            if shell_kw or (base == "os" and name in ("system", "popen")):
                out["shell"].append(where)
            if isinstance(func, ast.Name) and name in ("eval", "exec"):
                out["eval"].append(where)
            if base in ("pickle", "cPickle", "dill") and name in ("load", "loads", "Unpickler"):
                out["pickle"].append(where)
    return out


def _port_values(lines: list[str]):
    """(line number, mapping string) of every compose ``ports:`` entry."""
    in_block, indent = False, 0
    for n, raw in enumerate(lines, 1):
        code = raw.split("#")[0]
        stripped = code.strip()
        if stripped.startswith("ports:"):
            rest = stripped[len("ports:") :].strip()
            if rest.startswith("["):
                for m in re.finditer(r"['\"]?([^'\",\[\]\s]+)['\"]?", rest):
                    yield n, m.group(1)
                in_block = False
            else:
                in_block, indent = True, len(code) - len(code.lstrip())
            continue
        if in_block:
            if stripped.startswith("- "):
                yield n, stripped[2:].strip().strip("'\"")
            elif stripped and len(code) - len(code.lstrip()) <= indent:
                in_block = False


def scan_compose(root: Path) -> dict[str, Any]:
    out: dict[str, Any] = {"files": 0, "images": 0, "pinned": 0, "pending_marked": []}
    out.update(unpinned=[], port_mappings=0, db_ports_exposed=[], tls_config_lines=0)
    for f in sorted((root / "infra" / "compose").glob("*.y*ml")):
        out["files"] += 1
        lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
        for n, line in enumerate(lines, 1):
            m = COMPOSE_IMAGE.match(line)
            if m:
                out["images"] += 1
                where = f"{f.name}:{n} {m.group(1)}"
                if "@sha256:" in m.group(1):
                    out["pinned"] += 1
                elif "PENDING-FIRST-BUILD" in line:
                    out["pending_marked"].append(where)
                else:
                    out["unpinned"].append(where)
        for n, value in _port_values(lines):
            out["port_mappings"] += 1
            container = value.split(":")[-1].split("/")[0]
            if container in DB_CONTAINER_PORTS and not LOOPBACK_BIND.match(value):
                out["db_ports_exposed"].append(f"{f.name}:{n} {value}")
    for f in (root / "infra").rglob("*") if (root / "infra").is_dir() else []:
        if f.is_file() and f.suffix in {".yml", ".yaml", ".conf", ".tf", ".hcl", ".toml"}:
            out["tls_config_lines"] += len(
                TLS_CONFIG.findall(f.read_text(encoding="utf-8", errors="ignore"))
            )
    return out


def scan_dockerfile_bases(root: Path) -> dict[str, Any]:
    bases, unpinned = 0, []
    for d in ("services", "apps", "infra"):
        base = root / d
        if not base.is_dir():
            continue
        for f in base.rglob("Dockerfile*"):
            if SCAN_SKIP_PARTS & set(f.relative_to(root).parts) or not f.is_file():
                continue
            for n, line in enumerate(
                f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
            ):
                m = DOCKER_FROM.match(line)
                if m and not m.group(1).startswith("--"):
                    bases += 1
                    if "@sha256:" not in m.group(1):
                        unpinned.append(f"{_rel(f, root)}:{n} {m.group(1)}")
    return {"from_lines": bases, "unpinned": unpinned}


def scan_csrf_opt_outs(root: Path) -> dict[str, Any]:
    files = (
        [
            p
            for p in (root / "addons").rglob("controllers/*.py")
            if "__pycache__" not in p.parts and not _is_test_file(p.relative_to(root))
        ]
        if (root / "addons").is_dir()
        else []
    )
    opt_outs = [
        _rel(p, root)
        for p in files
        if re.search(r"csrf\s*=\s*False", p.read_text(encoding="utf-8", errors="ignore"))
    ]
    return {"controller_files": len(files), "opt_outs": opt_outs}


def count_forks(root: Path) -> int | None:
    forks = root / "FORKS.yaml"
    if not forks.is_file():
        return None
    body = [
        ln
        for ln in forks.read_text(encoding="utf-8").splitlines()
        if not ln.lstrip().startswith("#")
    ]
    return sum(1 for ln in body if re.match(r"^\s*-\s*repo\s*:", ln))


def sbom_components(root: Path) -> int | None:
    sbom = root / "sbom.cdx.json"
    if not sbom.is_file():
        return None
    try:
        return len(json.loads(sbom.read_text(encoding="utf-8")).get("components", []))
    except ValueError:
        return None


# --------------------------------------------------------- the vector checks --


def _probe_rejected(res: dict, jsonrpc: bool) -> bool | None:
    """True rejected / False served / None not exercised (unreachable or 404)."""
    if not res["reachable"] or res["status"] == 404:
        return None
    if res["status"] in (401, 403):
        return True
    if res["status"] in (301, 302, 303, 307, 308):
        return "/web/login" in res["location"]
    if jsonrpc:
        try:
            body = json.loads(res["body"])
        except ValueError:
            return False
        return isinstance(body, dict) and "error" in body and "result" not in body
    return False


def run_post_cutover_pentest_delta(
    root: Path = REPO_ROOT,
    http: Callable[..., dict] = http_request,
    fitness: Callable[[str], tuple[str, str]] = run_fitness,
    pytest_fn: Callable[[str], tuple[str, str]] = run_pytest,
    vendor_clean: Callable[[], tuple[int | None, str]] = run_vendor_clean,
) -> dict[str, Any]:
    """Measure the 24 vectors; finding counts are derived from FAILs."""
    out: dict[str, tuple[str, str]] = {}

    # -- live probes (read-only, unauthenticated) ------------------------------
    probes = {
        ("GET", "/my"): http("GET", "/my"),
        ("GET", "/odoo"): http("GET", "/odoo"),
        ("POST", "/seller/dashboard"): http("POST", "/seller/dashboard", jsonrpc=True),
        ("GET", "/non_existent_security_probe_endpoint"): http(
            "GET", "/non_existent_security_probe_endpoint"
        ),
    }
    auth_probes = [k for k in probes if k[1] != "/non_existent_security_probe_endpoint"]
    outcomes = {k: _probe_rejected(probes[k], jsonrpc=k[0] == "POST") for k in auth_probes}
    exercised = {k: v for k, v in outcomes.items() if v is not None}
    served = [f"{m} {p}" for (m, p), v in exercised.items() if v is False]
    if not exercised:
        unreachable = next((r.get("error") for r in probes.values() if not r["reachable"]), "")
        out["A01-01"] = (
            UNMEASURED,
            f"no protected route exercised ({unreachable or 'routes not mounted'}) at {ODOO_URL}",
        )
    else:
        out["A01-01"] = (
            FAIL if served else PASS,
            f"{len(exercised) - len(served)}/{len(exercised)} protected routes rejected an "
            f"unauthenticated request" + (f"; served: {', '.join(served)}" if served else ""),
        )

    reached = {k: r for k, r in probes.items() if r["reachable"] and r["status"] is not None}
    if not reached:
        out["A05-01"] = (UNMEASURED, f"{ODOO_URL} unreachable - error responses not exercised")
    else:
        leaks = [
            f"{m} {p} (HTTP {r['status']})"
            for (m, p), r in reached.items()
            if TRACEBACK_MARKER in r["body"]
        ]
        out["A05-01"] = (
            FAIL if leaks else PASS,
            f"{len(leaks)} of {len(reached)} unauthenticated error/redirect responses carry a "
            f"Python traceback" + (f": {', '.join(leaks)}" if leaks else ""),
        )

    # -- repo tests ------------------------------------------------------------
    for code, target in PYTEST_TARGETS.items():
        out[code] = pytest_fn(target)
    status, detail = out["A01-02"]
    out["A01-02"] = (status, detail + " (unit-level isolation tests; no live two-tenant probe)")

    out["A01-03"] = (
        UNMEASURED,
        "needs two authenticated portal identities to swap object ids; none available to this run",
    )

    # -- fitness checks ----------------------------------------------------------
    model_status, model_detail = fitness("check_model_registry.py")
    out["A01-04"] = (model_status, f"FF-20/21/22 {model_detail}")
    out["A09-01"] = (model_status, f"FF-20/21/22 {model_detail}")
    out["A02-02"] = fitness("check_ff09_residency.py")
    out["A05-02"] = fitness("check-lb06-analytics-readonly.py")

    # -- static scans ----------------------------------------------------------
    sec = scan_secrets(root)
    out["A02-01"] = (
        (FAIL if sec["hits"] else PASS) if sec["files_scanned"] else UNMEASURED,
        f"{len(sec['hits'])} secret pattern hit(s) in {sec['files_scanned']} source/config files"
        + (f": {_list(sec['hits'])}" if sec["hits"] else ""),
    )

    sinks = scan_python_sinks(root)
    scope = f"{sinks['files_scanned']} non-test Python files"
    for code, key, label in (
        (
            "A03-01",
            "sql",
            f"unreviewed execute() calls built by string formatting (of "
            f"{sinks['execute_calls']} execute calls; {len(sinks['sql_reviewed'])} more carry a "
            f"reviewed noqa: S608 justification)",
        ),
        ("A03-02", "shell", "shell=True / os.system / os.popen calls"),
        ("A03-03", "eval", "bare eval()/exec() calls"),
        ("A08-01", "pickle", "pickle/dill deserialisation calls"),
    ):
        hits = sinks[key]
        out[code] = (
            (FAIL if hits else PASS) if sinks["files_scanned"] else UNMEASURED,
            f"{len(hits)} {label} in {scope}" + (f": {_list(hits)}" if hits else ""),
        )

    compose = scan_compose(root)
    out["A02-03"] = (
        UNMEASURED,
        f"{compose['tls_config_lines']} TLS-version directives in infra/ specs; production "
        "edge/mesh TLS termination is not reachable from this workstation",
    )
    exposed = compose["db_ports_exposed"]
    out["A05-03"] = (
        (FAIL if exposed else PASS) if compose["files"] else UNMEASURED,
        f"{len(exposed)} DB/cache/analytics ports published beyond loopback across "
        f"{compose['port_mappings']} port mappings in {compose['files']} compose specs"
        + (f": {_list(exposed)}" if exposed else ""),
    )
    docker = scan_dockerfile_bases(root)
    unpinned = compose["unpinned"] + docker["unpinned"]
    out["A08-02"] = (
        (FAIL if unpinned else PASS) if compose["images"] or docker["from_lines"] else UNMEASURED,
        f"{compose['pinned']}/{compose['images']} compose images @sha256-pinned, "
        f"{len(compose['pending_marked'])} carry the PENDING-FIRST-BUILD marker (digest-pinning "
        f"policy); {docker['from_lines'] - len(docker['unpinned'])}/{docker['from_lines']} "
        f"Dockerfile FROM lines pinned" + (f"; unpinned: {_list(unpinned)}" if unpinned else ""),
    )

    csrf = scan_csrf_opt_outs(root)
    out["A07-01"] = (
        (FAIL if csrf["opt_outs"] else PASS) if csrf["controller_files"] else UNMEASURED,
        f"{len(csrf['opt_outs'])} csrf=False route opt-outs across {csrf['controller_files']} "
        "controller files" + (f": {_list(csrf['opt_outs'])}" if csrf["opt_outs"] else ""),
    )

    forks = count_forks(root)
    vc_code, vc_line = vendor_clean()
    if forks is None:
        out["A06-01"] = (FAIL, "FORKS.yaml missing")
    elif vc_code is None:
        out["A06-01"] = (
            UNMEASURED,
            f"FORKS.yaml entries: {forks}; vendor-clean not run: {vc_line}",
        )
    else:
        out["A06-01"] = (
            PASS if forks == 0 and vc_code == 0 else FAIL,
            f"FORKS.yaml entries: {forks}; check-vendor-clean exit {vc_code}: {vc_line}",
        )

    components = sbom_components(root)
    out["A06-02"] = (
        UNMEASURED,
        f"sbom.cdx.json components: {components if components is not None else 'no SBOM'}; "
        "the CVE lookup needs the OSV/NVD feeds (network) - no offline vulnerability database",
    )
    out["A07-02"] = (
        UNMEASURED,
        "needs an authenticated login against Odoo and the Next.js portals to observe session-id "
        "rotation; no test identity is available to this run",
    )
    out["A09-02"] = (
        UNMEASURED,
        "needs a live privileged action and inspection of the resulting audit records",
    )

    vectors = []
    for code, name, category, severity in VECTORS:
        status, details = out[code]
        vectors.append(
            {
                "code": code,
                "name": name,
                "category": category,
                "severity_if_failed": severity,
                "status": status,
                "details": details,
            }
        )
    failed = [v for v in vectors if v["status"] == FAIL]
    counts = {
        s.lower() + "_findings": sum(1 for v in failed if v["severity_if_failed"] == s)
        for s in SEVERITIES
    }
    return {
        "total_vectors": len(vectors),
        "passed": sum(1 for v in vectors if v["status"] == PASS),
        "failed": len(failed),
        "unmeasured": sum(1 for v in vectors if v["status"] == UNMEASURED),
        **counts,
        "vectors": vectors,
        "status": derive_verdict([v["status"] for v in vectors]),
    }


def execute_vault_secret_checks() -> dict[str, Any]:
    """EP-06 prod-mode refusal (local, measured); production rotation (unobservable)."""
    probe_path, probe_key = "unmapped/r11-security-review-probe", "api_key"
    env_var = f"FIX_SECRET_{probe_path.replace('/', '_').upper()}_{probe_key.upper()}"
    saved = {k: os.environ.get(k) for k in ("FIX_ENV", env_var)}
    detail = "EP-06: get_secret() returned a value in prod mode with no Vault-injected secret"
    ok = False
    try:
        VaultSecretManager.clear_cache()
        os.environ["FIX_ENV"] = "prod"
        os.environ.pop(env_var, None)
        try:
            VaultSecretManager.get_secret(probe_path, probe_key)
        except RuntimeError as exc:
            ok = "EP-06 VIOLATION" in str(exc)
            detail = (
                f"prod-mode get_secret() refused the plaintext fallback: {exc}" if ok else str(exc)
            )
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        VaultSecretManager.clear_cache()
    checks = {
        "ep06_prod_enforcement": {"status": PASS if ok else FAIL, "detail": detail},
        "production_secret_rotation": {
            "status": UNMEASURED,
            "scope": ROTATION_SCOPE,
            "reason": "no production Vault/OpenBao is reachable from this workstation; no "
            "rotation was performed or observed and no key fingerprints are available",
        },
    }
    return {"checks": checks, "status": derive_verdict([c["status"] for c in checks.values()])}


def verify_key_custody_transfer() -> dict[str, Any]:
    return {
        "scope": CUSTODY_SCOPE,
        "status": UNMEASURED,
        "reason": "dual-control HSM / key-shard / certificate custody handover is a human act; "
        "no signed custody register is observable here",
    }


def verify_wazuh_osquery_alerting(probe: Callable[[str, int], bool] = tcp_open) -> dict:
    open_ports = [p for p in WAZUH_PORTS if probe(WAZUH_HOST, p)]
    reason = (
        "Wazuh manager enrolment ports reachable, but agent enrolment, heartbeats and alert "
        "dispatch need the authenticated Wazuh API and the production agent fleet"
        if open_ports
        else f"Wazuh manager not reachable on {WAZUH_HOST}:{'/'.join(map(str, WAZUH_PORTS))} "
        "(compose profile msp not running); agents, heartbeats and alert dispatch unobservable"
    )
    return {"manager_ports_open": open_ports, "status": UNMEASURED, "reason": reason}


def build_report(pentest: dict, secrets: dict, custody: dict, wazuh: dict) -> dict[str, Any]:
    sections = {
        "pentest_delta": pentest["status"],
        "secret_handling": secrets["status"],
        "key_custody_transfer": custody["status"],
        "wazuh_osquery": wazuh["status"],
    }
    return {
        "task_id": "R11-M03-T01",
        "milestone": "R11-M03",
        "evaluated_at_utc": datetime.now(UTC).isoformat(),
        "standards": ["SC-009", "DoD-15", "ASVS Level 3", "NIST SP 800-115"],
        "target": ODOO_URL,
        "pentest_delta": pentest,
        "secret_rotation": secrets,
        "key_custody_transfer": custody,
        "wazuh_osquery": wazuh,
        "section_status": sections,
        "verdict": derive_verdict(list(sections.values())),
    }


def render_markdown(rep: dict[str, Any]) -> str:
    pt = rep["pentest_delta"]
    lines = [
        "# Production Security Closure Report (R11-M03-T01)",
        "",
        "**Document ID**: `SR-2026-10-R11-M03`  ",
        "**Governing Standards**: `SC-009` (Vulnerability & Pen-Test Management) · `DoD-15` (Zero High/Critical Findings)  ",
        f"**Evaluation Date**: {rep['evaluated_at_utc']}  ",
        f"**Computed Verdict**: **`{rep['verdict']}`** — {pt['critical_findings']} Critical, "
        f"{pt['high_findings']} High, {pt['medium_findings']} Medium findings; "
        f"{pt['unmeasured']} vectors UNMEASURED  ",
        "",
        "Every status below was measured by `tooling/scripts/run_r11_m03_security_review.py` in "
        f"this run against `{rep['target']}` and the repository (GV-009). UNMEASURED items need "
        "production access or a human act and keep the verdict from PASS.",
        "",
        "## 1. Summary",
        "",
        "| Assessment Stream | Result | Detail |",
        "|---|:---:|---|",
        f"| Penetration test delta | **{pt['status']}** | {pt['passed']} PASS / {pt['failed']} FAIL / "
        f"{pt['unmeasured']} UNMEASURED of {pt['total_vectors']} vectors |",
    ]
    for name, chk in rep["secret_rotation"]["checks"].items():
        lines.append(
            f"| Secrets: `{name}` | **{chk['status']}** | {chk.get('reason') or chk.get('detail')} |"
        )
    cu, wz = rep["key_custody_transfer"], rep["wazuh_osquery"]
    lines += [
        f"| Key custody handover | **{cu['status']}** | {cu['reason']} |",
        f"| Wazuh / osquery SIEM | **{wz['status']}** | {wz['reason']} |",
        "",
        "## 2. Penetration Test Delta Vectors",
        "",
        "| Code | Vector | Severity if failed | Result | Details |",
        "|---|---|:---:|:---:|---|",
    ]
    lines += [
        f"| `{v['code']}` | {v['name']} | {v['severity_if_failed']} | **{v['status']}** | "
        f"{v['details'].replace('|', '/')} |"
        for v in pt["vectors"]
    ]
    lines += [
        "",
        "## 3. Sign-off",
        "",
        "No sign-off is recorded by this tool. "
        + (
            "The computed verdict is PASS."
            if rep["verdict"] == PASS
            else f"The computed verdict is `{rep['verdict']}`; the closure condition (all vectors "
            "measured clean, rotation and custody evidenced) is not met."
        ),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):  # a cp1252 console must not crash the run
        sys.stdout.reconfigure(errors="replace")
    print("=" * 72)
    print("1000FiX ERP — Task R11-M03-T01: Final Security Review in Production")
    print("=" * 72)

    print("\n[1/4] Post-cutover penetration test delta (OWASP / ASVS L3)...")
    pentest = run_post_cutover_pentest_delta()
    for v in pentest["vectors"]:
        print(f"      [{v['status']}] {v['code']} {v['name']}: {v['details'][:160]}")

    print("\n[2/4] Vault secret handling (EP-06)...")
    secrets = execute_vault_secret_checks()
    for name, chk in secrets["checks"].items():
        print(f"      [{chk['status']}] {name}")

    print("\n[3/4] Key-material custody handover...")
    custody = verify_key_custody_transfer()
    print(f"      [{custody['status']}] {custody['reason']}")

    print("\n[4/4] Wazuh SIEM & osquery alerting...")
    wazuh = verify_wazuh_osquery_alerting()
    print(f"      [{wazuh['status']}] {wazuh['reason']}")

    report = build_report(pentest, secrets, custody, wazuh)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    json_path = EVIDENCE_DIR / "r11-m03-security-closure-report.json"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n[OK] Security evidence JSON written: {json_path}")

    md_path = DOCS_DIR / "r11-m03-security-closure-report.md"
    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(f"[OK] Security audit report written: {md_path}")
    print(
        f"\nVerdict: {report['verdict']} (pentest {pentest['passed']} PASS / {pentest['failed']} "
        f"FAIL / {pentest['unmeasured']} UNMEASURED)"
    )
    return exit_code_for(report["verdict"])


if __name__ == "__main__":
    started = time.perf_counter()
    code = main()
    print(f"elapsed {time.perf_counter() - started:.1f}s")
    sys.exit(code)
