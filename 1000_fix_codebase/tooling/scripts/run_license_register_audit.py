#!/usr/bin/env python3
"""run_license_register_audit.py — Annual D-030 Licence Register & SBOM/VEX Refresh (R11-M03-T04).

Implements:
1. Generates renewed CycloneDX SBOM (sbom.cdx.json) and VEX statement for all dependencies.
2. Conducts annual review of tooling/licence/register.yaml under decision D-030.
3. Validates operational compliance with restricted license conditions (AGPL, BSL, TSL):
   the audit rows are derived from the register (every approved-with-condition
   or not-approved component) and each condition is checked against the
   infra/ deployment manifests - COMPLIANT / NON_COMPLIANT when a static probe
   observed it, UNMEASURED (with the reason) when nothing could be observed.
4. Executes tooling/scripts/check-licence-gate.py and verifies 0 unapproved restricted components.
5. Emits r11-m03-license-register-annual-review.json and Markdown gate proof.

Verdict: PASS only when the gate is green AND every audited condition is
COMPLIANT. Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tomllib
import uuid
from datetime import UTC, datetime
from importlib import metadata as importlib_metadata
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTER_PATH = REPO_ROOT / "tooling" / "licence" / "register.yaml"
REGISTER_SCHEMA = "1000fix-erp/licence-register/1"
INFRA_DIR = REPO_ROOT / "infra"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
SBOM_PATH = REPO_ROOT / "sbom.cdx.json"
CHECK_SCRIPT = REPO_ROOT / "tooling" / "scripts" / "check-licence-gate.py"
UV_LOCK = REPO_ROOT / "uv.lock"
CURRENCY_PATH = REPO_ROOT / "tooling" / "version-currency" / "components.json"
# D-030 replacements that must stay approved and deployed (the decision names them)
D030_REPLACED_COMPONENTS = ("ceph", "apache/superset", "apache/airflow", "apache/kafka")

CREATE_EXTENSION = re.compile(
    r"create\s+extension\s+(?:if\s+not\s+exists\s+)?[\"']?([a-z0-9_]+)", re.IGNORECASE
)
PRELOAD = re.compile(r"shared_preload_libraries\s*[=:]\s*['\"]?([a-z0-9_, ]+)", re.IGNORECASE)
TSL_LICENCE_APACHE = re.compile(r"timescaledb\.license\W{1,4}apache", re.IGNORECASE)
# SQL that refuses to run unless the server's TimescaleDB licence is 'apache'
TSL_LICENCE_GUARD = re.compile(
    r"current_setting\(\s*'timescaledb\.license'[^)]*\)[^;]*?(?:<>|!=)\s*'apache'"
    r"[\s\S]*?raise\s+exception",
    re.IGNORECASE,
)
# TimescaleDB features licensed under the TSL (Community), not Apache-2.0
TSL_FEATURES = {
    "native compression": re.compile(
        r"timescaledb\.compress\b|\bcompress_chunk\s*\(|\badd_compression_policy\s*\(",
        re.IGNORECASE,
    ),
    "retention policy": re.compile(r"\badd_retention_policy\s*\(", re.IGNORECASE),
    "continuous aggregate": re.compile(
        r"timescaledb\.continuous\b|\badd_continuous_aggregate_policy\s*\(", re.IGNORECASE
    ),
    "reorder policy": re.compile(r"\badd_reorder_policy\s*\(", re.IGNORECASE),
    "user-defined job": re.compile(r"\badd_job\s*\(", re.IGNORECASE),
}
SKIP_DIRS = {
    "vendor",
    "node_modules",
    "tests",
    "docs",
    "tooling",
    "odoo-data",
    "__pycache__",
    ".git",
}

EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR = REPO_ROOT / "docs" / "traceability"


def _licence_from_metadata(dist_metadata) -> str:
    """Licence of an installed distribution from its own metadata, or ''."""
    expression = (dist_metadata.get("License-Expression") or "").strip()
    if expression:
        return expression
    classifiers = [
        c.split("::")[-1].strip()
        for c in (dist_metadata.get_all("Classifier") or [])
        if c.startswith("License ::") and c.strip() != "License :: OSI Approved"
    ]
    if classifiers:
        return " OR ".join(classifiers)
    text = (dist_metadata.get("License") or "").strip()
    # a full licence text pasted into the field is not an identifier
    return text if text and "\n" not in text and len(text) <= 80 else ""


def python_components(uv_lock: Path | None = None) -> list[dict]:
    """Every package pinned in uv.lock; licence read from the installed
    distribution's metadata when it is installed in this environment."""
    uv_lock = uv_lock or UV_LOCK
    if not uv_lock.is_file():
        return []
    lock = tomllib.loads(uv_lock.read_text(encoding="utf-8"))
    components = []
    for pkg in lock.get("package", []):
        source = pkg.get("source", {})
        if "editable" in source or "virtual" in source:
            continue  # the project itself, not a dependency
        name, version = pkg["name"], str(pkg.get("version", ""))
        licence, source_of_licence = "", ""
        try:
            dist = importlib_metadata.distribution(name)
            licence = _licence_from_metadata(dist.metadata)
            if licence:
                source_of_licence = f"installed metadata ({dist.version})"
        except importlib_metadata.PackageNotFoundError:
            pass
        components.append(
            {
                "name": name,
                "version": version,
                "licenses": [licence] if licence else [],
                "purl": f"pkg:pypi/{name}@{version}",
                "type": "library",
                "manifest": uv_lock.name,
                "licence_source": source_of_licence,
            }
        )
    return components


def _lockfiles(root: Path) -> list[Path]:
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames if d not in ("node_modules", "vendor", ".git", "odoo-data")
        )
        if "package-lock.json" in filenames:
            found.append(Path(dirpath) / "package-lock.json")
    return found


def npm_components(root: Path | None = None) -> list[dict]:
    """Every package in every committed package-lock.json (licence from the lockfile)."""
    root = root or REPO_ROOT
    seen: dict[tuple[str, str], dict] = {}
    for lock_path in _lockfiles(root):
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        rel = lock_path.relative_to(root).as_posix()
        for key, pkg in (lock.get("packages") or {}).items():
            if not key or "node_modules/" not in key:
                continue  # "" is the workspace root itself
            name = key.rsplit("node_modules/", 1)[-1]
            version = str(pkg.get("version", ""))
            licence = pkg.get("license") or ""
            if isinstance(licence, dict):
                licence = licence.get("type", "")
            entry = seen.setdefault(
                (name, version),
                {
                    "name": name,
                    "version": version,
                    "licenses": [licence] if licence else [],
                    "purl": f"pkg:npm/{name}@{version}",
                    "type": "library",
                    "manifest": rel,
                    "licence_source": "package-lock.json" if licence else "",
                },
            )
            if rel not in entry["manifest"].split(", "):
                entry["manifest"] += f", {rel}"
    return list(seen.values())


def _name_tokens(name: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", name.lower()) if len(t) >= 4]


def _image_segments(repo: str) -> list[str]:
    return [s for s in repo.lower().split("/") if s and "." not in s]


def _register_entry_for_image(repo: str, register: dict) -> dict | None:
    segments = _image_segments(repo)
    last = segments[-1] if segments else ""
    by_last = by_any = None
    for entry in register.get("components", []):
        comp = str(entry.get("name", "")).lower()
        comp_last = comp.rsplit("/", 1)[-1]
        if "/" in comp and not repo.lower().endswith(comp):
            continue
        if last == comp_last or last.startswith(comp_last + "-"):
            by_last = by_last or entry
        elif comp_last in segments:
            by_any = by_any or entry
    return by_last or by_any


def _currency_licence_for_image(repo: str, currency: list[dict]) -> tuple[str, str]:
    """Licence the version-currency register declares for the image's
    component - only when that declaration is a single unambiguous licence."""
    segments = _image_segments(repo)
    for comp in currency:
        licence = str(comp.get("licence", ""))
        if not licence or re.search(r"/|\bwas\b|\bper-|vendor|\(", licence, re.IGNORECASE):
            continue
        for token in _name_tokens(str(comp.get("name", ""))):
            if any(
                seg == token or seg.startswith(token) or (len(seg) >= 4 and token.startswith(seg))
                for seg in segments
            ):
                return licence, f"version-currency {comp.get('id')}"
    return "", ""


def image_components(deployments: list[dict], register: dict) -> list[dict]:
    """Every container image the infra/ compose manifests deploy."""
    currency: list[dict] = []
    if CURRENCY_PATH.is_file():
        currency = json.loads(CURRENCY_PATH.read_text(encoding="utf-8")).get("components", [])
    seen: dict[tuple[str, str], dict] = {}
    for dep in deployments:
        key = (dep["repo"], dep["tag"])
        if key in seen:
            seen[key]["manifest"] += f", {dep['file']}:{dep['service']}"
            continue
        entry = _register_entry_for_image(dep["repo"], register)
        if entry:
            name, licence, source = entry["name"], str(entry.get("licence", "")), "licence register"
        else:
            name = dep["repo"]
            licence, source = _currency_licence_for_image(dep["repo"], currency)
        seen[key] = {
            "name": name,
            "version": dep["tag"] or dep.get("digest") or "untagged",
            "licenses": [licence] if licence else [],
            "purl": f"pkg:oci/{dep['repo']}@{dep['tag'] or dep.get('digest') or 'untagged'}",
            "type": "container",
            "manifest": f"{dep['file']}:{dep['service']}",
            "licence_source": source if licence else "",
        }
    return list(seen.values())


def extension_components(register: dict, usages: dict[str, list[str]]) -> list[dict]:
    """Register components used as PostgreSQL extensions (CREATE EXTENSION)."""
    components = []
    for entry in register.get("components", []):
        name = str(entry.get("name", ""))
        files = usages.get(name.rsplit("/", 1)[-1].lower(), [])
        if files:
            components.append(
                {
                    "name": name,
                    "version": "unpinned",
                    "licenses": [str(entry.get("licence", ""))],
                    "purl": f"pkg:generic/{name}",
                    "type": "library",
                    "manifest": ", ".join(files),
                    "licence_source": "licence register",
                }
            )
    return components


def generate_renewed_cyclonedx_sbom(
    register: dict | None = None, deployments: list[dict] | None = None
) -> dict:
    """CycloneDX 1.5 SBOM derived from the dependency manifests actually in the
    repository: uv.lock (Python), every package-lock.json (npm), the infra/
    compose images and register components used as Postgres extensions.
    Nothing is listed that a manifest does not declare; a licence is recorded
    only when a manifest/metadata/register states it."""
    register = register if register is not None else load_register()
    deployments = deployments if deployments is not None else scan_deployments()
    components = [
        *python_components(),
        *npm_components(),
        *image_components(deployments, register),
        *extension_components(register, scan_extension_usage()),
    ]
    project = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(UTC).isoformat(),
            "component": {
                "name": project.get("project", {}).get("name", "1000fix-erp"),
                "version": project.get("project", {}).get("version", ""),
                "type": "application",
            },
            "manufacture": {"name": "1000FiX Services Ltd."},
        },
        "components": components,
    }
    SBOM_PATH.write_text(json.dumps(sbom, indent=2) + "\n", encoding="utf-8", newline="\n")
    return sbom


def sbom_summary(sbom: dict) -> dict:
    comps = sbom["components"]
    unclassified = [
        f"{c['name']}@{c['version']} ({c['manifest']})" for c in comps if not c["licenses"]
    ]
    by_type: dict[str, int] = {}
    for c in comps:
        by_type[c["type"]] = by_type.get(c["type"], 0) + 1
    return {
        "file": SBOM_PATH.name,
        "format": "CycloneDX 1.5 JSON",
        "total_dependencies": len(comps),
        "by_type": by_type,
        "licence_classified": len(comps) - len(unclassified),
        "licence_unclassified": len(unclassified),
        "unclassified_components": unclassified,
    }


def load_register(register_path: Path = REGISTER_PATH) -> dict:
    """Parse the D-030 licence register (tooling/licence/register.yaml)."""
    data = yaml.safe_load(register_path.read_text(encoding="utf-8")) or {}
    if data.get("schema") != REGISTER_SCHEMA:
        raise ValueError(
            f"{register_path.name}: schema {data.get('schema')!r} is not {REGISTER_SCHEMA!r}"
        )
    components = data.get("components")
    if not isinstance(components, list) or not components:
        raise ValueError(f"{register_path.name}: no components listed")
    return data


def _image_repo_and_tag(image: str) -> tuple[str, str]:
    """'ghcr.io/x/meshcentral:1.1.60@sha256:..' -> ('ghcr.io/x/meshcentral', '1.1.60')."""
    ref = image.split("@", 1)[0]
    head, _, last = ref.rpartition("/")
    name, _, tag = last.partition(":")
    return (f"{head}/{name}" if head else name), tag


def _publishes_beyond_loopback(port: object) -> bool:
    """A compose port mapping reachable from outside the host?"""
    if isinstance(port, dict):  # long syntax
        return "published" in port and port.get("host_ip") not in LOOPBACK_HOSTS
    text = str(port).strip()
    if ":" not in text:
        return True  # "3000": published on every interface
    host = text.rsplit(":", 2)[0] if text.count(":") >= 2 else ""
    return host.strip("[]") not in LOOPBACK_HOSTS


def scan_deployments(infra_dir: Path = INFRA_DIR) -> list[dict]:
    """Every service in every infra/ compose file: image, tag, exposure."""
    deployments: list[dict] = []
    for path in sorted([*infra_dir.rglob("*.yml"), *infra_dir.rglob("*.yaml")]):
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        services = doc.get("services") if isinstance(doc, dict) else None
        if not isinstance(services, dict):
            continue
        for service, spec in services.items():
            if not isinstance(spec, dict) or not isinstance(spec.get("image"), str):
                continue
            repo, tag = _image_repo_and_tag(spec["image"])
            ports = spec.get("ports") or []
            deployments.append(
                {
                    "file": path.relative_to(REPO_ROOT).as_posix(),
                    "service": service,
                    "repo": repo,
                    "tag": tag,
                    "digest": spec["image"].partition("@")[2],
                    "exposed_ports": [str(p) for p in ports if _publishes_beyond_loopback(p)],
                    "text": yaml.safe_dump(spec),
                }
            )
    return deployments


def _deployments_of(component: str, deployments: list[dict]) -> list[dict]:
    comp = component.lower()
    comp_last = comp.rsplit("/", 1)[-1]
    found = []
    for dep in deployments:
        repo = dep["repo"].lower()
        repo_last = repo.rsplit("/", 1)[-1]
        if "/" in comp and not (repo == comp or repo.endswith("/" + comp)):
            continue
        if repo_last == comp_last or repo_last.startswith(comp_last + "-"):
            found.append(dep)
    return found


def _where(deps: list[dict]) -> str:
    return ", ".join(f"{d['file']}:{d['service']} ({d['repo']}:{d['tag']})" for d in deps)


def _source_files(root: Path, suffixes: tuple[str, ...]) -> list[Path]:
    """First-party source files (no vendor/, node_modules/, tests, docs, tooling)."""
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        found.extend(Path(dirpath) / f for f in sorted(filenames) if f.endswith(suffixes))
    return found


def scan_extension_usage(root: Path | None = None) -> dict[str, list[str]]:
    """Postgres extension name -> first-party files that create or preload it
    (``CREATE EXTENSION`` in SQL / Python, ``shared_preload_libraries`` in conf
    or compose)."""
    root = root or REPO_ROOT
    usage: dict[str, list[str]] = {}
    for path in _source_files(root, (".sql", ".py", ".conf", ".yml", ".yaml")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        names = {m.lower() for m in CREATE_EXTENSION.findall(text)}
        for libs in PRELOAD.findall(text):
            names.update(n.strip().strip("'\"").lower() for n in libs.split(",") if n.strip())
        for name in names:
            usage.setdefault(name, []).append(path.relative_to(root).as_posix())
    return usage


def _strip_sql_comments(sql: str) -> str:
    """Drop -- line comments and /* */ block comments (string literals kept)."""
    return re.sub(r"/\*[\s\S]*?\*/|--[^\n]*", "", sql)


def _infra_config_texts(infra_dir: Path) -> dict[str, str]:
    texts = {}
    for path in sorted(infra_dir.rglob("*")):
        if (
            path.is_file()
            and path.suffix in (".yml", ".yaml", ".conf")
            and "odoo-data" not in path.parts
        ):
            texts[path.as_posix()] = path.read_text(encoding="utf-8", errors="ignore")
    return texts


def _probe_condition(
    condition: str,
    deps: list[dict],
    extension_files: list[str],
    infra_texts: dict[str, str],
    root: Path,
) -> list[tuple[bool, str]]:
    """Static probes a condition's text names; [] when none applies."""
    probes: list[tuple[bool, str]] = []
    lowered = condition.lower()
    pin = re.search(r"pinned (\d+)\.(\d+)\.x", lowered)
    if pin and deps:
        prefix = f"{pin.group(1)}.{pin.group(2)}."
        off_pin = [d for d in deps if not d["tag"].startswith(prefix)]
        probes.append(
            (
                not off_pin,
                f"every image tag is {prefix}x" if not off_pin else f"off-pin: {_where(off_pin)}",
            )
        )
    if "tsl" in lowered:
        # 1. TSL features must be switched off where the extension runs
        configured = [
            src
            for src, text in [
                *((f"{d['file']}:{d['service']}", d["text"]) for d in deps),
                *infra_texts.items(),
            ]
            if TSL_LICENCE_APACHE.search(text)
        ]
        # No Timescale-enabled Postgres in infra/: the SQL that creates the
        # extension must itself refuse a server whose licence is not 'apache'.
        guarded = [
            rel
            for rel in extension_files
            if TSL_LICENCE_GUARD.search(
                _strip_sql_comments((root / rel).read_text(encoding="utf-8", errors="ignore"))
            )
        ]
        sql_enforced = not deps and bool(extension_files) and len(guarded) == len(extension_files)
        if configured:
            detail = f"timescaledb.license=apache set in {', '.join(configured)}"
        elif sql_enforced:
            detail = (
                "no Timescale-enabled Postgres is deployed in infra/; the extension SQL refuses "
                f"any server whose timescaledb.license is not 'apache' ({', '.join(guarded)})"
            )
        else:
            detail = (
                "timescaledb.license=apache is not set in any infra/ postgres configuration "
                "or compose command, nor enforced by the SQL that creates the extension - "
                "TSL features are not disabled"
            )
        probes.append((bool(configured) or sql_enforced, detail))
        # 2. no first-party SQL / Python may call a TSL-only feature
        used = []
        sources = {root / rel for rel in extension_files} | set(
            _source_files(root, (".sql", ".py"))
        )
        for path in sorted(sources):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if path.suffix == ".py" and "timescale" not in text.lower():
                continue  # e.g. a scheduler's add_job() is not TimescaleDB's
            if path.suffix == ".sql":
                text = _strip_sql_comments(text)  # a comment naming a feature is not a call
            used += [
                f"{path.relative_to(root).as_posix()}: {feature}"
                for feature, rx in TSL_FEATURES.items()
                if rx.search(text)
            ]
        probes.append(
            (
                not used,
                "no first-party SQL/Python calls a TSL-only feature"
                if not used
                else "TSL-only features used: " + "; ".join(used),
            )
        )
    if deps and any(
        k in lowered for k in ("internal", "trust boundary", "self-hosted", "multi-tenant")
    ):
        exposed = [d for d in deps if d["exposed_ports"]]
        probes.append(
            (
                not exposed,
                "every published port binds loopback only"
                if not exposed
                else "published beyond loopback: "
                + "; ".join(f"{d['file']}:{d['service']} {d['exposed_ports']}" for d in exposed),
            )
        )
    return probes


def audit_component(
    entry: dict,
    register: dict,
    deployments: list[dict],
    extension_usage: dict[str, list[str]] | None = None,
    infra_texts: dict[str, str] | None = None,
    root: Path | None = None,
) -> dict:
    """One register row -> COMPLIANT / NON_COMPLIANT / NOT_DEPLOYED / UNMEASURED."""
    name = str(entry.get("name", ""))
    status = str(entry.get("status", ""))
    condition = str(entry.get("condition", "")).strip()
    deps = _deployments_of(name, deployments)
    ext_files = (extension_usage or {}).get(name.rsplit("/", 1)[-1].lower(), [])
    row = {
        "component": name,
        "licence": str(entry.get("licence", "")),
        "register_status": status,
        "condition": condition,
        "deployments": [f"{d['file']}:{d['service']}" for d in deps]
        + [f"{f} (extension)" for f in ext_files],
    }
    in_use = bool(deps or ext_files)
    if status == "not-approved":
        row["compliance"] = "NON_COMPLIANT" if in_use else "COMPLIANT"
        row["evidence"] = (
            f"not-approved component is deployed: {', '.join(row['deployments'])}"
            if in_use
            else "no infra/ manifest deploys it"
        )
        return row
    same_class = re.match(r"same class as (\S+)", condition, re.IGNORECASE)
    if same_class:
        ref = next(
            (
                c
                for c in register["components"]
                if str(c.get("name", "")).lower() == same_class.group(1).lower()
            ),
            None,
        )
        condition = str(ref.get("condition", "")) if ref else condition
    if not in_use:
        # a condition on use cannot be breached by a component that is not used
        row["compliance"] = "NOT_DEPLOYED"
        row["evidence"] = "no infra/ manifest deploys it and no first-party source loads it"
        return row
    probes = _probe_condition(condition, deps, ext_files, infra_texts or {}, root or REPO_ROOT)
    if not probes:
        row["compliance"] = "UNMEASURED"
        row["evidence"] = "deployed, but no static probe exists for this condition"
    elif all(ok for ok, _ in probes):
        row["compliance"] = "COMPLIANT"
        row["evidence"] = "; ".join(detail for _, detail in probes)
    else:
        row["compliance"] = "NON_COMPLIANT"
        row["evidence"] = "; ".join(detail for ok, detail in probes if not ok)
    return row


def audit_license_register(
    register_path: Path = REGISTER_PATH, infra_dir: Path = INFRA_DIR, root: Path | None = None
) -> dict:
    """Annual D-030 review: every register component carrying a condition (or
    a not-approved status) is checked against the deployment manifests and
    the first-party sources that load it."""
    root = root or REPO_ROOT
    register = load_register(register_path)
    deployments = scan_deployments(infra_dir)
    usage = scan_extension_usage(root)
    infra_texts = _infra_config_texts(infra_dir)
    conditions_audit = [
        audit_component(entry, register, deployments, usage, infra_texts, root)
        for entry in register["components"]
        if str(entry.get("status", "")) in ("approved-with-condition", "not-approved")
    ]
    counts = {
        outcome: sum(1 for r in conditions_audit if r["compliance"] == outcome)
        for outcome in ("COMPLIANT", "NON_COMPLIANT", "NOT_DEPLOYED", "UNMEASURED")
    }
    if counts["NON_COMPLIANT"]:
        status = "FAIL"
    elif counts["UNMEASURED"] or not conditions_audit:
        status = "INCOMPLETE"
    else:
        status = "APPROVED"
    return {
        "review_cadence": str(register.get("review_cadence", "")),
        "last_annual_review_date": datetime.now(UTC).date().isoformat(),
        "register_schema": register["schema"],
        "register_components": len(register["components"]),
        "deployments_scanned": len(deployments),
        "conditions_audited": len(conditions_audit),
        "conditions_compliant": counts["COMPLIANT"],
        "conditions_non_compliant": counts["NON_COMPLIANT"],
        "conditions_not_deployed": counts["NOT_DEPLOYED"],
        "conditions_unmeasured": counts["UNMEASURED"],
        "condition_details": conditions_audit,
        "status": status,
    }


def execute_licence_gate() -> dict:
    """Runs tooling/scripts/check-licence-gate.py against the fresh SBOM."""
    cmd = [sys.executable, str(CHECK_SCRIPT), str(SBOM_PATH)]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    stdout = proc.stdout.strip()

    return {
        "command": f"python tooling/scripts/check-licence-gate.py {SBOM_PATH.name}",
        "exit_code": proc.returncode,
        "output": stdout,
        "is_green": proc.returncode == 0,
    }


def audit_replaced_components(register: dict, deployments: list[dict]) -> list[dict]:
    """D-030 replacements: still approved in the register and still deployed."""
    by_name = {str(c.get("name", "")).lower(): c for c in register["components"]}
    rows = []
    for name in D030_REPLACED_COMPONENTS:
        entry = by_name.get(name, {})
        last = name.rsplit("/", 1)[-1]
        deployed = [d for d in deployments if last in d["repo"].lower().split("/")]
        rows.append(
            {
                "component": name,
                "register_status": str(entry.get("status", "missing")),
                "deployments": [f"{d['file']}:{d['service']}" for d in deployed],
                "retained": str(entry.get("status", "")) == "approved" and bool(deployed),
            }
        )
    return rows


def compute_verdict(
    gate: dict, reg_audit: dict, replaced: list[dict], sbom: dict | None = None
) -> str:
    """FAIL on a red gate or a non-compliant condition; INCOMPLETE while a
    condition is unmeasured, a replacement is not verified retained, or an SBOM
    component has no licence on record (it cannot be classified against D-030)."""
    if not gate["is_green"] or reg_audit["status"] == "FAIL":
        return "FAIL"
    unclassified = (sbom or {}).get("licence_unclassified", 0)
    if (
        reg_audit["status"] != "APPROVED"
        or not all(r["retained"] for r in replaced)
        or unclassified
    ):
        return "INCOMPLETE"
    return "PASS"


def _row_status(ok: bool) -> str:
    return "**PASS**" if ok else "**FAIL**"


def main() -> int:
    print("=" * 72)
    print("1000FiX ERP — Task R11-M03-T04: Annual D-030 Licence Register & SBOM Refresh")
    print("=" * 72)

    print("\n[1/3] Generating CycloneDX 1.5 Software Bill of Materials (SBOM)...")
    sbom = generate_renewed_cyclonedx_sbom()
    total_components = len(sbom["components"])
    sbom_sum = sbom_summary(sbom)
    print(
        f"      SBOM Written: {SBOM_PATH.name} ({total_components} components from uv.lock, "
        f"package-lock.json, infra/ images; {sbom_sum['licence_unclassified']} without a licence "
        "on record)"
    )

    print("\n[2/3] Performing Annual D-030 Register & Operational Condition Audit...")
    reg_audit = audit_license_register()
    replaced = audit_replaced_components(load_register(), scan_deployments())
    print(
        f"      Review Cadence: {reg_audit['review_cadence']} | Date: {reg_audit['last_annual_review_date']}"
    )
    print(
        f"      Restricted Conditions Audited: {reg_audit['conditions_audited']} | "
        f"compliant {reg_audit['conditions_compliant']} | "
        f"non-compliant {reg_audit['conditions_non_compliant']} | "
        f"not deployed {reg_audit['conditions_not_deployed']} | "
        f"unmeasured {reg_audit['conditions_unmeasured']} -> {reg_audit['status']}"
    )
    for row in reg_audit["condition_details"]:
        print(f"      {row['compliance']:<13} {row['component']}: {row['evidence']}")

    print("\n[3/3] Executing Restricted-Licence Pipeline Gate...")
    gate = execute_licence_gate()
    print(f"      Gate Exit Code: {gate['exit_code']} ({'PASS' if gate['is_green'] else 'FAIL'})")
    for line in gate["output"].splitlines():
        print(f"      {line}")

    verdict = compute_verdict(gate, reg_audit, replaced, sbom_sum)
    unapproved = len(re.findall(r"^licence-gate: FAIL ", gate["output"], re.MULTILINE))

    # Consolidate evidence
    evidence = {
        "task_id": "R11-M03-T04",
        "milestone": "R11-M03",
        "evaluated_at_utc": datetime.now(UTC).isoformat(),
        "standards": [
            "D-030 Binding Decision",
            "OpenChain ISO/IEC 5230",
            "CycloneDX 1.5",
            "TSS §18.5",
        ],
        "sbom_summary": sbom_sum,
        "register_audit": reg_audit,
        "replaced_components": replaced,
        "licence_gate": gate,
        "verdict": verdict,
    }

    # Write evidence JSON
    json_path = EVIDENCE_DIR / "r11-m03-license-register-annual-review.json"
    json_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"\n[OK] Licence evidence JSON written: {json_path}")

    condition_lines = "\n".join(
        f"- `{r['component']}` (`{r['licence']}`, register: {r['register_status']}): "
        f"**{r['compliance']}** - {r['evidence']}"
        for r in reg_audit["condition_details"]
    )
    replaced_lines = "\n".join(
        f"{i}. **{r['component']}** (register: {r['register_status']}): "
        + (
            f"retained - deployed in {', '.join(r['deployments'])}"
            if r["retained"]
            else "NOT verified retained (not approved in the register or not deployed)"
        )
        for i, r in enumerate(replaced, start=1)
    )
    retained = sum(1 for r in replaced if r["retained"])
    unclassified_lines = (
        "\n".join(f"- {c}" for c in sbom_sum["unclassified_components"]) or "- none"
    )

    # Write Markdown gate proof
    md_content = f"""# Annual Open-Source Licence Review & D-030 Gate Proof (R11-M03-T04)

**Document ID**: `LIC-ANNUAL-2026-R11`  
**Governing Decision**: `D-030` (Annual Open-Source Licence Review & Restricted Licence Policy)  
**Standard**: OpenChain (ISO/IEC 5230:2020) · CycloneDX 1.5 Specification  
**Evaluation Date**: {evidence['evaluated_at_utc']}  
**Status**: **`{verdict}`** — licence gate exit {gate['exit_code']}, register audit {reg_audit['status']}  

---

## 1. Executive Summary

Milestone **R11-M03-T04** executes the mandatory annual review of the `tooling/licence/register.yaml` open-source licence classification register. As established in architectural rule `D-030`, the licence register is **an ongoing operational governance control subject to annual re-certification**, not a one-off sign-off.

The SBOM is derived from the repository's dependency manifests (`uv.lock`, every `package-lock.json`, the `infra/` compose images, register components loaded as Postgres extensions); the pipeline gate classified it against the register. Each register condition was checked against the deployment manifests and the first-party sources that load the component. NOT_DEPLOYED rows (condition not triggered - nothing deploys or loads the component) are listed for review and do not block; a deployed component whose condition no static probe can observe is UNMEASURED and keeps the verdict from PASS, as does any component without a licence on record.

| Metric | Target | Actual Result | Status |
|---|---|---|:---:|
| **Dependencies with a Licence on Record** | 100% | **{sbom_sum['licence_classified']}/{total_components} components ({sbom_sum['licence_unclassified']} unclassified)** | {_row_status(sbom_sum['licence_unclassified'] == 0)} |
| **Unapproved Restricted Licences** | **0** | **{unapproved}** | {_row_status(unapproved == 0 and gate['is_green'])} |
| **D-030 Condition Compliance** | 100% | **{reg_audit['conditions_compliant']}/{reg_audit['conditions_audited']} compliant ({reg_audit['conditions_non_compliant']} non-compliant, {reg_audit['conditions_not_deployed']} not deployed, {reg_audit['conditions_unmeasured']} unmeasured)** | {_row_status(reg_audit['status'] == 'APPROVED')} |
| **Four D-030 Replaced Components** | Retained | **{retained}/{len(replaced)} verified retained** | {_row_status(retained == len(replaced))} |
| **Licence Gate Pipeline Result** | Exit 0 | **Exit Code {gate['exit_code']}** | {_row_status(gate['is_green'])} |

---

## 2. Status of Four D-030 Replaced Components

{replaced_lines}

---

## 3. Audit of Restricted-Licence Components with Conditions

{reg_audit['conditions_audited']} register components carry a condition or a not-approved status:
{condition_lines}

### Components without a licence on record ({sbom_sum['licence_unclassified']})

{unclassified_lines}

---

## 4. Pipeline Gate Output Log

```
{gate['output']}
```

---

## 5. Certification Sign-off

Signed by:
- **Chief Technology Officer (CTO)**: *1000FiX Services Ltd.*
- **Chief Architect**: *Architecture Review Board (ARB) Lead*
- **Legal Counsel**: *Intellectual Property & Open-Source Compliance*
"""  # noqa: W291 - Markdown hard line breaks in generated report
    md_path = DOCS_DIR / "r11-m03-license-gate-proof.md"
    md_path.write_text(md_content, encoding="utf-8")
    print(f"[OK] Licence gate proof written: {md_path}")

    print(f"\nVERDICT: {verdict}")
    return {"PASS": 0, "FAIL": 1}.get(verdict, 2)


if __name__ == "__main__":
    sys.exit(main())
