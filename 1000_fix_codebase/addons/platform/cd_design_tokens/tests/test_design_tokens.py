"""cd_design_tokens tests — FF-23 companion for the R1 carrier.

The module ships no models; what it must guarantee is that its generated
assets are fresh, complete and token-pure. These tests run the same
assertions as the CFM suite so a stale or hand-edited realisation fails at
module level too, not only in CI.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
REPO = MODULE.parents[2]
SOURCE = REPO / "libs/ts/ui/src/tokens/tokens.json"
SCSS = MODULE / "static/src/tokens.scss"
CSS = MODULE / "static/src/tokens.css"
COMPONENTS = MODULE / "static/src/components"


def flat_tokens() -> dict[str, str]:
    def walk(node: dict, prefix: str = "") -> dict[str, str]:
        out: dict[str, str] = {}
        for key in sorted(node):
            if key.startswith("$"):
                continue
            child = node[key]
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(child, dict) and "$value" in child:
                out[path] = str(child["$value"])
            elif isinstance(child, dict):
                out.update(walk(child, path))
        return out

    with open(SOURCE, encoding="utf-8") as handle:
        return walk(json.load(handle))


class TestGeneratedAssets(unittest.TestCase):
    def test_generator_header_present_and_do_not_edit(self):
        text = SCSS.read_text(encoding="utf-8")
        self.assertIn("GENERATED", text)
        self.assertIn("DO NOT EDIT", text)

    def test_every_token_in_source_is_in_scss(self):
        text = SCSS.read_text(encoding="utf-8")
        for path, value in flat_tokens().items():
            self.assertIn(f"${path.replace('.', '-').lower()}: {value};", text, path)

    def test_every_token_in_source_is_in_css(self):
        text = CSS.read_text(encoding="utf-8")
        for path, value in flat_tokens().items():
            self.assertIn(f"--fix-{path.replace('.', '-').lower()}: {value};", text, path)

    def test_bengali_stack_is_first_class(self):
        text = SCSS.read_text(encoding="utf-8")
        self.assertIn("$typography-font-bengali-family: Noto Sans Bengali;", text)


class TestComponentPurity(unittest.TestCase):
    RAW_COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgb[a]?\(")
    RAW_SIZE = re.compile(r"\b\d+(\.\d+)?(px|rem|em|pt)\b")

    def test_components_contain_no_raw_literals(self):
        for partial in sorted(COMPONENTS.glob("*.scss")):
            for line_no, line in enumerate(partial.read_text(encoding="utf-8").splitlines(), 1):
                code = line.split("//")[0]
                self.assertIsNone(self.RAW_COLOR.search(code), f"{partial.name}:{line_no}")
                self.assertIsNone(self.RAW_SIZE.search(code), f"{partial.name}:{line_no} {code}")

    def test_components_reference_only_declared_tokens(self):
        declared = {f"${path.replace('.', '-').lower()}" for path in flat_tokens()}
        for partial in sorted(COMPONENTS.glob("*.scss")):
            for ref in re.findall(r"\$[a-z0-9-]+", partial.read_text(encoding="utf-8")):
                self.assertIn(ref, declared, f"{partial.name}: unknown token {ref}")


if __name__ == "__main__":
    unittest.main()
