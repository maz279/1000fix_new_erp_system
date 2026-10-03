#!/usr/bin/env python3
"""as0203-codemod — add AS-02/AS-03 conformance to Wave-5 models.

Adds missing chatter inheritance and operating_unit_id fields to every
model flagged by the registry check. Only touches modules whose models
are missing these fields; existing fields are never duplicated.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CHATTER = '_inherit = ["mail.thread", "mail.activity.mixin"]'
OU_FIELD = 'operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")'


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text
    # Find each class definition; add chatter/OU right after _description or _inherit lines
    def patch_class(match: re.Match) -> str:
        block = match.group(0)
        header = match.group(1)  # "class X(models.Model):\n    ..."
        body = block

        # Detect existing chatter
        has_chatter = bool(re.search(r'mail\.thread', block))
        # Detect existing operating_unit_id
        has_ou = bool(re.search(r'operating_unit_id\s*=\s*fields\.', block))

        # Insert after the _inherit/_name/_description/_order block
        # Find where field definitions start (first "xxx = fields." line)
        field_match = re.search(r'\n(\s{4}\w+\s*=\s*fields\.)', block)
        if not field_match:
            return block

        insert_at = field_match.start(1)
        additions = []
        if not has_chatter:
            additions.append(CHATTER)
        if not has_ou:
            additions.append(OU_FIELD)
        if not additions:
            return block

        insert_text = ("\n    " + "\n    ".join(additions) + "\n")
        body = block[:insert_at] + insert_text.lstrip("\n") + "\n    " + block[insert_at:]
        return body

    # Match class definitions with their body (up to next class or EOF)
    result = re.sub(
        r'(class\s+\w+\(models\.Model\):\n(?:    """[\s\S]*?"""\n)?(?:    _\w+\s*=\s*[^\n]+\n)+)',
        patch_class, text)

    if result != orig:
        path.write_text(result, encoding="utf-8")
        return True
    return False


def main() -> int:
    changed = 0
    for mod in REPO.rglob("addons/domain/*/cd_*/models/*.py"):
        if "__pycache__" in str(mod):
            continue
        if patch_file(mod):
            print(f"[ ok ] {mod.relative_to(REPO)}")
            changed += 1
    print(f"as0203-codemod: {changed} file(s) patched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
