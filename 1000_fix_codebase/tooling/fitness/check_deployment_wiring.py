#!/usr/bin/env python3
"""check_deployment_wiring - FF-48: every built piece is actually wired in.

The A03 workflow audit (2026-11-03, R10) found code that passed its unit
tests and never ran in production, because the thing that runs it was
missing:
  * cron methods with no ir.cron record (cron_monitor_service_level, the
    CRM QBR/renewal jobs) - a test calls the method directly, so it passes;
  * events published with no consumer anywhere (party.merged,
    complaint.escalated_72h, journey.lead_requested);
  * workspace buttons calling actions that do not exist (action_engage,
    action_renew) or that the surface whitelist refuses
    ("Action not available for this surface").

This check finds all four statically, without a database:
  cron_without_record    a `cron_*` method no data XML calls
  event_without_consumer an event type published with no in-Odoo consumer
                         (fix.event.consumer data record) and no external
                         consumer (the type string appears in services/)
  surface_action_missing a SURFACES actions entry the model does not define
  button_not_allowed     a P03 fragment button whose action the model's
                         surface does not whitelist

It is a RATCHET. Known gaps live in
evidence/deployment_wiring_baseline.json. A NEW gap fails the check, and a
baseline entry that has been fixed also fails, until it is removed, so the
list only shrinks. Refresh it deliberately with --update-baseline.

Exit 0 clean - 1 new gaps, or fixed gaps still in the baseline.
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADDONS = ROOT / "addons"
BASELINE = Path(__file__).resolve().parent / "evidence" / "deployment_wiring_baseline.json"
VENDOR_MODEL_ROOTS = [
    ROOT / "vendor" / "odoo" / "addons",
    ROOT / "vendor" / "odoo" / "odoo" / "addons",
    ROOT / "vendor" / "oca",
]
CATEGORIES = (
    "cron_without_record",
    "event_without_consumer",
    "surface_action_missing",
    "button_not_allowed",
)


SKIP_DIRS = {
    "tests",
    "__pycache__",
    ".mimosa",
    "migrations",
    "node_modules",
    ".venv",
    "dist",
    "build",
}


def _skip(path: Path) -> bool:
    return bool(set(path.parts) & SKIP_DIRS)


def _walk(root: Path, suffixes: tuple[str, ...]):
    """Files under root, never descending into skipped directories."""
    for here, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for name in files:
            if name.endswith(suffixes):
                yield Path(here) / name


def _py_files(root: Path):
    yield from _walk(root, (".py",))


def _parse(path: Path):
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return None


def _strs(node) -> list[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.List | ast.Tuple | ast.Set):
        return [
            e.value for e in node.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)
        ]
    return []


# --- model -> methods (static) ---------------------------------------------
def model_methods() -> dict[str, set[str]]:
    own: dict[str, set[str]] = {}
    parents: dict[str, set[str]] = {}
    base: set[str] = set()
    orm = ROOT / "vendor" / "odoo" / "odoo" / "orm" / "models.py"
    # Vendor code contributes model methods only from its models/ packages.
    vendor = [
        f for r in VENDOR_MODEL_ROOTS if r.exists() for f in _py_files(r) if "models" in f.parts
    ]
    files = [orm, *_py_files(ADDONS), *vendor]
    for path in files:
        tree = _parse(path)
        if tree is None:
            continue
        for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            if path == orm and cls.name == "BaseModel":
                base |= {
                    f.name
                    for f in cls.body
                    if isinstance(f, ast.FunctionDef | ast.AsyncFunctionDef)
                }
                continue
            name, inherit = None, []
            for stmt in cls.body:
                if (
                    isinstance(stmt, ast.Assign)
                    and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Name)
                ):
                    if stmt.targets[0].id == "_name":
                        found = _strs(stmt.value)
                        name = found[0] if found else None
                    elif stmt.targets[0].id == "_inherit":
                        inherit = _strs(stmt.value)
            methods = {
                f.name for f in cls.body if isinstance(f, ast.FunctionDef | ast.AsyncFunctionDef)
            }
            targets = [name] if name else inherit
            for model in targets:
                own.setdefault(model, set()).update(methods)
                parents.setdefault(model, set()).update(p for p in inherit if p != model)
    # Every model also gets the `base` model's extensions (mail, web...).
    base |= own.get("base", set())
    resolved: dict[str, set[str]] = {}

    def resolve(model: str, seen: frozenset = frozenset()) -> set[str]:
        if model in resolved:
            return resolved[model]
        out = set(own.get(model, set())) | base
        for parent in parents.get(model, ()):
            if parent not in seen:
                out |= resolve(parent, seen | {model})
        resolved[model] = out
        return out

    return {m: resolve(m) for m in own}


# --- SURFACES and fragments --------------------------------------------------
def _eval_actions(node) -> set[str] | None:
    if isinstance(node, ast.Set | ast.List | ast.Tuple):
        return set(_strs(node))
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in ("set", "frozenset")
    ):
        return set(_strs(node.args[0])) if node.args else set()
    return None


def surfaces() -> dict[str, tuple[set[str], str]]:
    out: dict[str, tuple[set[str], str]] = {}
    for path in sorted((ADDONS / "platform" / "cd_p03_portal" / "controllers").glob("a*/m*.py")):
        tree = _parse(path)
        if tree is None:
            continue
        for stmt in tree.body:
            if not (
                isinstance(stmt, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "SURFACES" for t in stmt.targets)
                and isinstance(stmt.value, ast.Dict)
            ):
                continue
            for key, conf in zip(stmt.value.keys, stmt.value.values, strict=False):
                if not (isinstance(key, ast.Constant) and isinstance(conf, ast.Dict)):
                    continue
                actions: set[str] = set()
                for k, v in zip(conf.keys, conf.values, strict=False):
                    if isinstance(k, ast.Constant) and k.value == "actions":
                        actions = _eval_actions(v) or set()
                rel = path.relative_to(ROOT).as_posix()
                prev = out.get(key.value, (set(), rel))
                out[key.value] = (prev[0] | actions, rel)
    return out


SCREEN = re.compile(r"^[ \t]{2,6}'([A-Za-z0-9:_-]+)':\s*\{", re.M)
MODEL = re.compile(r"\bmodel:\s*'([a-z0-9_.]+)'")
BUTTON = re.compile(r"\{\s*m:\s*'([a-z0-9_]+)'")


def fragment_buttons():
    static = ADDONS / "platform" / "cd_p03_portal" / "static" / "src"
    for js in sorted(static.glob("a*/m*.js")):
        text = js.read_text(encoding="utf-8")
        starts = [(m.start(), m.group(1)) for m in SCREEN.finditer(text)]
        for i, (pos, sid) in enumerate(starts):
            body = text[pos : starts[i + 1][0] if i + 1 < len(starts) else len(text)]
            model = MODEL.search(body)
            if not model:
                continue
            for button in BUTTON.findall(body):
                yield js.relative_to(ROOT).as_posix(), sid, model.group(1), button


# --- crons and events ---------------------------------------------------------
def cron_gaps() -> set[str]:
    called = set()
    for xml in _walk(ADDONS, (".xml",)):
        called |= set(
            re.findall(r"model\.(\w+)\(", xml.read_text(encoding="utf-8", errors="replace"))
        )
    gaps = set()
    for path in _py_files(ADDONS):
        tree = _parse(path)
        if tree is None:
            continue
        for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            for fn in cls.body:
                if (
                    isinstance(fn, ast.FunctionDef)
                    and fn.name.startswith(("cron_", "_cron_"))
                    and fn.name not in called
                ):
                    gaps.add("%s:%s.%s" % (path.relative_to(ROOT).as_posix(), cls.name, fn.name))
    return gaps


def published_events() -> dict[str, str]:
    out: dict[str, str] = {}
    for path in _py_files(ADDONS):
        tree = _parse(path)
        if tree is None:
            continue
        for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
            fname = (
                call.func.id if isinstance(call.func, ast.Name) else getattr(call.func, "attr", "")
            )
            idx = 1 if fname == "publish" else 0 if fname == "emit" else None
            if idx is None or len(call.args) <= idx:
                continue
            arg = call.args[idx]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and "." in arg.value:
                out.setdefault(arg.value, path.relative_to(ROOT).as_posix())
    return out


def consumed_events() -> tuple[set[str], set[str]]:
    exact, prefixes = set(), set()
    pattern = re.compile(
        r'model="fix\.event\.consumer".*?<field name="event_type">([^<]+)</field>', re.S
    )
    for xml in _walk(ADDONS, (".xml",)):
        for etype in pattern.findall(xml.read_text(encoding="utf-8", errors="replace")):
            etype = etype.strip()
            (prefixes if etype.endswith(".*") else exact).add(etype.rstrip("*"))
    return exact, prefixes


def external_mentions(types: set[str]) -> set[str]:
    services = ROOT / "services"
    if not services.exists():
        return set()
    blob = []
    for path in _walk(services, (".py", ".ts", ".js", ".json", ".yaml", ".yml")):
        if "test" not in path.name:
            blob.append(path.read_text(encoding="utf-8", errors="replace"))
    text = "\n".join(blob)
    return {t for t in types if t in text}


def findings() -> dict[str, set[str]]:
    methods = model_methods()
    surf = surfaces()
    result = {c: set() for c in CATEGORIES}
    result["cron_without_record"] = cron_gaps()
    events = published_events()
    exact, prefixes = consumed_events()
    external = external_mentions(set(events))
    result["event_without_consumer"] = {
        t
        for t in events
        if t not in exact and t not in external and not any(t.startswith(p) for p in prefixes)
    }
    for model, (actions, rel) in surf.items():
        known = methods.get(model)
        if known is None:
            continue  # a model defined outside the scanned roots
        for action in actions - known:
            result["surface_action_missing"].add("%s:%s (%s)" % (model, action, rel))
    for rel, sid, model, button in fragment_buttons():
        allowed = surf.get(model, (set(), ""))[0]
        if button not in allowed:
            result["button_not_allowed"].add("%s:%s:%s:%s" % (rel, sid, model, button))
    return result


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    found = findings()
    if "--update-baseline" in argv:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(
            json.dumps({c: sorted(found[c]) for c in CATEGORIES}, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(
            "check_deployment_wiring: baseline written (%s)"
            % ", ".join("%s=%d" % (c, len(found[c])) for c in CATEGORIES)
        )
        return 0
    baseline = json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else {}
    new, fixed = {}, {}
    for c in CATEGORIES:
        known = set(baseline.get(c, []))
        new[c] = sorted(found[c] - known)
        fixed[c] = sorted(known - found[c])
    bad = any(new.values()) or any(fixed.values())
    for c in CATEGORIES:
        for item in new[c]:
            print("NEW   %s: %s" % (c, item))
        for item in fixed[c]:
            print("FIXED %s: %s (remove it from the baseline)" % (c, item))
    summary = ", ".join("%s=%d" % (c, len(found[c])) for c in CATEGORIES)
    if bad:
        print("check_deployment_wiring: FAIL - %s" % summary)
        print(
            "  remedy: wire the new gap (ir.cron / fix.event.consumer / SURFACES actions), or, for a fixed"
        )
        print("  one, run python tooling/fitness/check_deployment_wiring.py --update-baseline")
        return 1
    print("check_deployment_wiring: OK - %s (all known, none new)" % summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
