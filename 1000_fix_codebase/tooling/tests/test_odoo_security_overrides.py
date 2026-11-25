"""tooling/ci/odoo-security-overrides.txt stays consistent with uv.lock (R01 re-audit).

CI installs Odoo's requirements on top of `uv sync` with these overrides; the
security job then proves the environment still matches the lock
(`uv sync --frozen --inexact --check`). This is the fast, static half of that
proof: a package pinned in BOTH files must carry the SAME version, or the Odoo
install downgrades a locked package and `uv run` silently re-syncs it - the
mixed environment of finding B (pyOpenSSL 24.1.0 next to cryptography 50).
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

CODE = Path(__file__).resolve().parents[2]
OVERRIDES = CODE / "tooling" / "ci" / "odoo-security-overrides.txt"
# extra runtime packages the Odoo image installs next to Odoo's requirements
IMAGE_EXTRAS = CODE / "infra" / "docker" / "odoo" / "requirements-first-party.txt"
LOCK = CODE / "uv.lock"
NEVER = "sys_platform == 'never'"


def _norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _overrides(path: Path = OVERRIDES) -> list[tuple[str, str | None, str]]:
    """(name, pinned version or None, marker) for every requirement line."""
    out = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        req, _, marker = (part.strip() for part in line.partition(";"))
        name, sep, version = req.partition("==")
        out.append((_norm(name), version.strip() if sep else None, marker))
    return out


def _locked() -> dict[str, set[str]]:
    lock = tomllib.loads(LOCK.read_text(encoding="utf-8"))
    versions: dict[str, set[str]] = {}
    for pkg in lock.get("package", []):
        if "version" in pkg:
            versions.setdefault(_norm(pkg["name"]), set()).add(pkg["version"])
    return versions


def test_every_override_is_an_exact_pin_or_a_removal() -> None:
    entries = _overrides()
    assert entries, "no overrides parsed"
    loose = [n for n, v, m in entries if v is None and m != NEVER]
    assert not loose, f"overrides must pin exactly (==) or remove ({NEVER}): {loose}"


def test_overrides_agree_with_the_uv_lock() -> None:
    locked = _locked()
    drift = {
        name: (version, sorted(locked[name]))
        for name, version, _ in _overrides()
        if version and name in locked and version not in locked[name]
    }
    assert not drift, "override != uv.lock version (re-pin the override to the lock): " + ", ".join(
        f"{n} override {v} vs lock {lk}" for n, (v, lk) in drift.items()
    )


def test_image_extras_are_exact_lock_pins() -> None:
    locked = _locked()
    extras = _overrides(IMAGE_EXTRAS)
    assert extras, "no image extras parsed"
    wrong = [
        (name, version)
        for name, version, _ in extras
        if version is None or version not in locked.get(name, set())
    ]
    assert not wrong, f"image extras must pin the uv.lock version: {wrong}"


def test_shared_crypto_stack_is_overridden() -> None:
    # The packages Odoo pins AND the lock carries must all be overridden;
    # otherwise Odoo's pin silently wins on install (finding B).
    pinned = {name for name, version, _ in _overrides() if version}
    required = {"cryptography", "lxml", "idna", "requests", "urllib3", "pyopenssl"}
    assert required <= pinned, f"missing overrides: {sorted(required - pinned)}"
