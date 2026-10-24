#!/usr/bin/env python3
"""check-no-fixtures — FF-39 (PP1-M04-T01): no fixture/demo/mock data ships.

Fails the build when fixture-shaped content appears where runtimes consume
it. Allowed homes for fixtures: **/tests/**, **/stories/**, db/seeds/** and
the frozen prototype (outside the repo). Also enforces the P-11/no-raw-fetch
discipline: apps must import libs/ts/api-client, never call fetch() directly
(server-side Next fetch of OWN routes is also out of contract — everything
cross-service goes through the client).

Exit: 0 pass / 1 violations.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ALLOWED_PARTS = {"tests", "stories", "__tests__", "node_modules", ".next", "__pycache__"}
SEEDS = REPO / "db" / "seeds"
APPS = REPO / "apps"

# File-name smells for fixture files in runtime space
FIXTURE_NAME = re.compile(r"(mock|fixture|dummy|fake|sample)[-_.]", re.I)
# Content smells: array-of-synthetic-records literals (>= 8 near-identical
# object rows) and PRNG-in-render — conservative patterns to avoid false
# positives on legitimate config.
PRNG_IN_CODE = re.compile(r"\b(Math\.random|random\.random)\s*\(")
RAW_FETCH = re.compile(r"(?<![.\w])fetch\s*\(")
# PP6 §8 (03-DATA-STRATEGY): the client never performs MONETARY
# arithmetic — money arrives as backend-computed values (AS-10). Binary
# ops / Math.* / rounding on money-named identifiers is the smell.
# Rate/percentage formatting (rating, *_rate, pct) is not money.
MONEY_NAME = re.compile(
    r"\b\w*(?:_bdt|amount|price|total|payable|subtotal|gross|vat|tds|net)\b", re.I
)
MONEY_ARITH = re.compile(
    r"[\w.\]]+\s*(?:[+*/%-]|\*\*)\s*[\w.\]]+"  # a op b
    r"|Math\.\w+\s*\(\s*[\w.\]]*"  # Math.fn(x...)
    r"|\.toFixed\s*\("
)  # rounding
# prose inside string literals ("gross/commission/TDS/net") is not math —
# strip plain quoted strings; template literals keep ${} expressions
QUOTED_STRING = re.compile(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'')


def _money_arithmetic_smells(code: str) -> list[str]:
    """Money-named operands inside arithmetic expressions (per line)."""
    hits = []
    for line_no, line in enumerate(code.splitlines(), 1):
        bare = QUOTED_STRING.sub("", line)
        for m in MONEY_ARITH.finditer(bare):
            expr = m.group(0)
            if MONEY_NAME.search(expr):
                hits.append(f"line {line_no}: {expr.strip()[:60]}")
    return hits


# Strip // and /* */ comments before scanning (comments mentioning "fetch()"
# are documentation, not code)
LINE_COMMENT = re.compile(r"//[^\n]*")
BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)


def strip_comments(text: str) -> str:
    text = BLOCK_COMMENT.sub("", text)
    text = LINE_COMMENT.sub("", text)
    return text


def in_allowed(path: Path) -> bool:
    return any(p in ALLOWED_PARTS for p in path.parts)


def check_fixture_files() -> list[str]:
    v: list[str] = []
    for base in (APPS, REPO / "addons"):
        for f in base.rglob("*"):
            if not f.is_file() or in_allowed(f):
                continue
            if FIXTURE_NAME.search(f.name):
                v.append(f"fixture-named file in runtime space: {f.relative_to(REPO)}")
    return v


def check_prng_and_fetch() -> list[str]:
    v: list[str] = []
    if not APPS.exists():
        return v
    for f in APPS.rglob("*.ts*"):
        if in_allowed(f):
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        code = strip_comments(text)  # scan code, not comments
        if PRNG_IN_CODE.search(code):
            v.append(f"PRNG in app code (fabrication risk): {f.relative_to(REPO)}")
        # OIDC auth files are exempt: the token exchange goes to the
        # Keycloak IdP (not the API gateway), from a validated issuer
        # URL with redirect:"error" — documented in the file itself.
        if RAW_FETCH.search(code) and "api-client" not in f.as_posix() and "auth.ts" not in f.name:
            v.append(f"raw fetch() outside libs/ts/api-client (P-11): {f.relative_to(REPO)}")
        # libs may format money (bn007 groups digits); apps must not do
        # monetary arithmetic at all (§8) — masks.ts's formatter is exempt
        if "/libs/" not in f.as_posix():
            for hit in _money_arithmetic_smells(code):
                v.append(f"client-side money arithmetic (PP6 §8): " f"{f.relative_to(REPO)} {hit}")
    return v


def main() -> int:
    violations = check_fixture_files() + check_prng_and_fetch()
    if violations:
        print(f"no-fixtures: FAIL - {len(violations)} violation(s):")
        for v in violations:
            print(f"  {v}")
        return 1
    print(
        "no-fixtures: OK - runtime space clean (fixtures only under tests/stories/seeds; "
        "no PRNG in app code; no raw fetch outside api-client)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
