# migrate-sql-constraints.py - one-shot codemod (P07 live-install finding).
#
# Odoo 19 REMOVED `_sql_constraints`; the loader warns
# "Model attribute '_sql_constraints' is no longer supported, please define
# models.Constraint on the model" and the constraints are NOT created - a
# silent estate-wide loss of unique/check enforcement. This codemod rewrites
# every first-party model:
#
#     _sql_constraints = [
#         ("code_unique", "unique(code)", "Code must be unique"),
#     ]
# ->
#     code_unique = models.Constraint("UNIQUE (code)", "Code must be unique")
#
# AST-driven (messages may contain parentheses/quotes; regex is not safe).
# Idempotent: files without _sql_constraints are untouched.
from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADDONS = REPO / "addons"


def transform_def(definition: str) -> str:
    """unique(a,b) -> UNIQUE (a,b); check(x) -> CHECK (x)."""
    d = definition.strip()
    for kw in ("unique", "check"):
        if d.startswith(kw):
            inner = d[len(kw) :].strip()
            return f"{kw.upper()} {inner}"
    return d.upper()


def rewrite_file(path: Path) -> bool:
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        print(f"[FAIL] {path}: syntax error {e}")
        return False
    lines = src.splitlines(keepends=True)
    edits: list[
        tuple[int, int, list[str]]
    ] = []  # (start_line, end_line, new_lines) 1-based inclusive
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for stmt in node.body:
            if not (
                isinstance(stmt, ast.Assign)
                and any(
                    isinstance(t, ast.Name) and t.id == "_sql_constraints" for t in stmt.targets
                )
            ):
                continue
            if not isinstance(stmt.value, ast.List):
                continue
            indent = " " * stmt.col_offset
            new_lines = [
                f"{indent}# Odoo 19 dropped the legacy constraint tuple list;\n"
                f"{indent}# constraints are models.Constraint attributes\n"
                f"{indent}# (migrated by tooling/scripts/migrate-sql-constraints.py)\n"
            ]
            ok = True
            for el in stmt.value.elts:
                if not (isinstance(el, ast.Tuple) and len(el.elts) == 3):
                    ok = False
                    break
                name = el.elts[0].value
                definition = el.elts[1].value
                message = el.elts[2].value
                if not (
                    isinstance(name, str)
                    and isinstance(definition, str)
                    and isinstance(message, str)
                ):
                    ok = False
                    break
                new_lines.append(
                    f"{indent}_{name} = models.Constraint("
                    f"{transform_def(definition)!r}, {message!r})\n"
                )
            if not ok:
                print(
                    f"[SKIP] {path.name}: non-literal tuple in _sql_constraints - migrate by hand"
                )
                continue
            edits.append((stmt.lineno, stmt.end_lineno or stmt.lineno, new_lines))
    if not edits:
        return True
    for start, end, new in sorted(edits, reverse=True):
        lines[start - 1 : end] = new
    path.write_text("".join(lines), encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    for mod in ADDONS.rglob("models"):
        if not mod.is_dir():
            continue
        for py in mod.glob("*.py"):
            if "_sql_constraints" not in py.read_text(encoding="utf-8", errors="replace"):
                continue
            before = py.read_text(encoding="utf-8")
            if not rewrite_file(py):
                return 1
            if py.read_text(encoding="utf-8") != before:
                changed += 1
                print(f"[ ok ] {py.relative_to(REPO)}")
    # any left?
    left = [
        p
        for p in ADDONS.rglob("*.py")
        if "models" in p.parts
        and "_sql_constraints" in p.read_text(encoding="utf-8", errors="replace")
    ]
    if left:
        print(f"migrate-sql-constraints: {len(left)} file(s) still carry _sql_constraints:")
        for p in left:
            print(f"  {p.relative_to(REPO)}")
        return 1
    print(f"migrate-sql-constraints: done - {changed} model file(s) rewritten to models.Constraint")
    return 0


if __name__ == "__main__":
    sys.exit(main())
